%% Основной файл обновленной матмодели
%
clc; close all; clearvars;
%
now_string = datestr(now,'yyyy_mm_dd_HH_MM_SS');
%
movement_setup;
%
fid = fopen('generator_log.txt', 'a+');
fprintf(fid, '%s\n', 'Generating random trajectory...');
fclose(fid);
pause(1);
%
% mod_size = 360000;
%
options1 = {'r_lim', r_lim, 't_lim', t_lim, 'v_lim', v_lim, 'a', flagAccel, 'p', Puniform};
[A_det, route_array, v_vector, course_vector] = maneuvre_acceleration_generator_func(dt, course, V0, mod_size, options1);
%
timestep = (1:size(A_det, 2)) * dt - dt; % Временная шкала
N = length(timestep); % Длина векторов сгенерированных данных
%
fid = fopen('generator_log.txt', 'a+');
fprintf(fid, '%s\n', 'Generating random motion component...');
fclose(fid);
pause(1);
% Параметры волн
wave_F = 1 / params.wave_t;%0.5;%0.25;
wave_A = 2 * params.wave_h;%8;%5;
flt_len = 40;
mean_T = 500;
options2 = {'F', wave_F, 'A', wave_A, 'flt_len', flt_len, 'T', mean_T, 'log', true};
E_rand = random_ship_motion_generator_func(timestep, options2);
for i = 1:size(E_rand, 2)
    E_rand(:, i) = vrq(E_rand(:, i), q0);
end
%
cA0 = [0 0 0]';
cE = padarray([0 0 0]', [0 N-1], 'post');
cU = padarray([0 0 0]', [0 N-1], 'post');
%
cA = padarray(cA0, [0 N-1], 'post');
if flagAccel == 0
    cV = padarray(cV0, [0 N-1], 'post');
else
    cV = padarray([0 0 0]', [0 N-1], 'post');
end
cP = padarray(cP0, [0 N-1], 'post');
cW = padarray(cW0, [0 N-1], 'post');
cWtot = padarray(cW0, [0 N-1], 'post');
cG = padarray(g, [0 N-1], 'post');
cAg = padarray(g + cA0, [0 N-1], 'post');
cRPY = padarray(cU0, [0 N-1], 'post');
%
RFx_array = padarray(vrq([1 0 0]', q0), [0 N-1], 'post');
RFy_array = padarray(vrq([0 1 0]', q0), [0 N-1], 'post');
%
% Точки
pV_set = zeros(num_pts, 3, N);
pA_set = zeros(num_pts, 3, N);
pR_set = zeros(num_pts, 3, N);
pP_set = zeros(num_pts, 3, N);
for i = 1:num_pts
    pR_set(i, :, 1) = vrq(point_set0(:, i), q0);
    pP_set(i, :, 1) = squeeze(pR_set(i, :, 1))' + cP(:, 1);
end
%
% Генерация
%
cnt = 0;
%
fid = fopen('generator_log.txt', 'a+');
fprintf(fid, '%s\n', 'Generating movement parameters...');
fclose(fid);
pause(1);
for i = 2:N
    cA(:, i) = A_det(:, i-1);
    cV(:, i) = cV(:, i-1) + cA(:, i) * dt;
    cP(:, i) = cP(:, i-1) + cV(:, i) * dt;   
    %
    if (i == 2) && (flagAccel == 1)
        cU(:, i) = [0 0 0]';
    else
        cU(:, i) = cross(cV(:, i-1), cV(:, i)) / norm(cV(:, i-1)) / norm(cV(:, i));
    end 
    qd = w2quat(cU(:, i));
    %
    cE(:, i) = vrq(E_rand(:, i-1), qd);
    cW(:, i) = cW(:, i-1) + cE(:, i) * dt;
    %
    qw = w2quat(cW(:, i));
    q = qxq(qw, qd);
    %
    RFx_array(:, i) = vrq(RFx_array(:, i-1), q);
    RFy_array(:, i) = vrq(RFy_array(:, i-1), q);
    %
    cWtot(:, i) = quat2w(q) / dt;
    %
    pitch = - asin(RFx_array(3, i) / norm(RFx_array(:, i)));
    roll = asin(RFy_array(3, i) / norm(RFy_array(:, i)));
    yaw = mod(atan2(RFx_array(2, i), RFx_array(1, i)), 2 * pi);
    %
    gx = dot(RFx_array(:, i), g) / norm(RFx_array(:, i));
    gy = dot(RFy_array(:, i), g) / norm(RFy_array(:, i));
    gz = sqrt(g0^2 - gx^2 - gy^2);
    %
    cG(:, i) = [gx gy gz]'; 
    cRPY(:, i) = [roll pitch yaw]';
    cAg(:, i) = cA(:, i) + cG(:, i);
    %
    for j = 1:num_pts
        R = squeeze(pR_set(j, :, i-1))';
        pR_set(j, :, i) = vrq(R, q);
        pP_set(j, :, i) = cP(:, i) + R;    
        WXR = cross(cWtot(:, i-1), R);
        pV_set(j, :, i) = cV(:, i-1) + WXR;
        WWXR = cross(cWtot(:, i-1), WXR);
        EXR = cross(cE(:, i-1), R);
        pA_set(j, :, i) = cAg(:, i-1) + WWXR + EXR;
    end
    %
    if (i / N * 100) > cnt
        cnt = cnt + 1;
        fid = fopen('generator_log.txt', 'a+');
        fprintf(fid, '%d\n', cnt);
        fclose(fid);
    end    
end
%
figure(1); clf; hold all; grid on;
plot(timestep, RFx_array');
plot(timestep, RFy_array');
title(strcat('Wave F: ', num2str(wave_F), ',    Wave A: ', num2str(wave_A)));
%% Зашумление всех данных
%
fid = fopen('generator_log.txt', 'a+');
fprintf(fid, '%s\n', 'Adding sensor noise...');
fclose(fid);
pause(1);
data_table = cell(length(sensors), length(param_set));
shift_cnt = 0;
for i = 1:length(sensors)
    for j = 1:sensors{i}.n_params
        name = sensors{i}.param{j}.name;
        k = get_param_idx(name);
        switch name
            case {'ax', 'ay', 'az'}
                out = add_alavar_noise_single_channel_func(squeeze(pA_set(i, axis_num(k), :)), ...
                                                           sensors{i}.param{j}.nbk(1), ...
                                                           sensors{i}.param{j}.nbk(2), ...
                                                           sensors{i}.param{j}.nbk(3), ...
                                                           sensors{i}.param{j}.scale);                                                        
            case {'ux', 'uy', 'uz'}
                out = squeeze(cRPY(axis_num(k), :))' + randn(N, 1) * sensors{i}.param{j}.sigma;
            case {'gx', 'gy', 'gz'}
                out = squeeze(pP_set(i, axis_num(k), :)) + randn(N, 1) * sensors{i}.param{j}.sigma;                
            case {'vx', 'vy', 'vz'}
                out = squeeze(pV_set(i, axis_num(k), :)) + randn(N, 1) * sensors{i}.param{j}.sigma;
            case {'wx', 'wy', 'wz'}
                out = add_alavar_noise_single_channel_func(cWtot(axis_num(k), :)', ...
                                                           sensors{i}.param{j}.nbk(1), ...
                                                           sensors{i}.param{j}.nbk(2), ...
                                                           sensors{i}.param{j}.nbk(3), ...
                                                           sensors{i}.param{j}.scale);                                                      
            otherwise
                continue;
        end
        % Прореживание данных
        if sensors{i}.dt > dt
            t_out = timestep(1):sensors{i}.dt:timestep(end);
            tsin = timeseries(out, timestep);
            tsout = resample(tsin, t_out);
            data_table{i,k} = [round(t_out', 3), tsout.Data];
        else
            data_table{i,k} = [round(timestep', 3), out];
        end
    end
end
%
%% формирование спутниковых данных
% (преобразование в географические координаты)
%
pbtyGroupPass = params.srns_loss_prob;%
if pbtyGroupPass > 0
    modeGroupPass = 1;
else
    modeGroupPass = 0;
end
minT = params.srns_loss_time.min;%
maxT = params.srns_loss_time.max;%
%
lengthT = 0;
countSensors = length(sensors);
indx_1 = 0;
indx_2 = 0;
for i = 1:countSensors
    if strcmp(sensors{i}.type, 'srns')
        indx_2 = get_param_idx(sensors{i}.param{1}.name);
        indx_1 = i;
        lengthT = size(data_table{indx_1, indx_2}, 1);
        break;
    end
end
matrixTime = 0:(lengthT-1);
%       
if(modeGroupPass == 1.0)  
    flagP = 1;
    timeP = randi([minT maxT]);
    count = 1;
    countForGNSS = 1;
    while  count <= lengthT
        if(timeP < 1)
                timeP = randi([minT maxT]);
                genP = randi([0 100]);
                flagP = 0;
                if (genP <= pbtyGroupPass*100)
                    flagP = 1;
                end   
        end
        if (flagP  ==  1)
            for m = 1:countSensors
                if strcmp(sensors{m}.type, 'srns')
                    data_table{m, get_param_idx('gx')}(count, :) = [];
                    data_table{m, get_param_idx('gy')}(count, :) = [];
                    data_table{m, get_param_idx('gz')}(count, :) = [];
                end
            end
        else
            count = count + 1;
        end
        countForGNSS = countForGNSS+1;
        lengthT = size(data_table{indx_1, indx_2}, 1);
        timeP = timeP - 1;
    end
end
%
for i = 1:length(sensors)
    if strcmp(sensors{i}.type, 'srns')
        k = get_param_idx(sensors{i}.param{1}.name);
        xyz = zeros(size(data_table{i, k}, 1), 3);
        xyz(:, axis_num(k)) = data_table{i, k}(:, 2);
        for j = 2:sensors{i}.n_params
            k = get_param_idx(sensors{i}.param{j}.name);        
            xyz(:, j) = data_table{i, k}(:, 2);
        end
        defMiss = sensors{i}.prob;%
        newTime = data_table{i, get_param_idx('gx')}(:, 1);
        count = 1;
        countForGNSS = 1;
        while  count <= size(xyz, 1)
            det = randi([0 100]);
            if (0 < det && det  <= (defMiss * 100))
                xyz(count,:) = [];
                newTime(count,:) = [];
            else
                count = count + 1;  
            end
            countForGNSS = countForGNSS + 1;
        end
        [lat, lon, h] = ned2geodetic(xyz(:, 1), xyz(:, 2), xyz(:, 3), ...
                                     location0(1), location0(2), location0(3), ...
                                     sensors{i}.ell);      
        data_table{i, get_param_idx('gx')} = [newTime lat];
        data_table{i, get_param_idx('gy')} = [newTime lon];
        data_table{i, get_param_idx('gz')} = [newTime h];
    end
end
%
%% формирование данных лага (модуля горизонтальной скорости)
param_set = [param_set, 'vgnd'];
data_table = [data_table, cell(length(sensors), 1)];
%
for i = 1:length(sensors)
    if strcmp(sensors{i}.type, 'lag')
        k = get_param_idx(sensors{i}.param{1}.name);
        xy = zeros(size(data_table{i, k}, 1), 2);
        times = data_table{i, k}(:, 1);
        xy(:, 1) = data_table{i, k}(:, 2);%
        data_table{i, k} = []; % удаляем компоненты горизонтальной скорости
        k = get_param_idx(sensors{i}.param{2}.name);        
        xy(:, 2) = data_table{i, k}(:, 2);%  + point_set(2, i);
        data_table{i, k} = []; % удаляем компоненты горизонтальной скорости
        data_table{i, end} = [times, vecnorm(xy, 2, 2)];
    end
end
%
%% Сохранение
%
fid = fopen('generator_log.txt', 'a+');
fprintf(fid, '%s\n', 'Saving data...');
fclose(fid);
pause(1);
%%
if ~isempty(save_path)
    if save_path(end) ~= '/'
        save_path = strcat(save_path, '/');
    end
else
    save_path = '/';
end
target_folder = strcat(save_path, now_string, '/');
mkdir(target_folder);
%%
gcf = figure;
set(gcf, 'Visible', 'off');
plot(cP(2, :), cP(1, :), 'LineWidth', 3);
pbaspect([1 1 1]);
daspect([1 1 1]);
xlabel('Координата Х, м');
ylabel('Координата Y, м');
ax = gca;
ax.YAxis.Exponent = 0;
ax.XAxis.Exponent = 0;
grid on;
%
saveas(gcf, strcat(target_folder, now_string, '_Model_Trajectory.png'));
close(gcf);
%%
%
mat_name = strcat(save_path, 'last_run.mat');
%
hdf5name = strcat(target_folder, now_string, '_ref.hdf5');
h5create(hdf5name, '/ts' ,size(timestep));
h5write(hdf5name, '/ts', timestep);
h5create(hdf5name, '/E_rand', size(E_rand));
h5write(hdf5name, '/E_rand', E_rand);
h5create(hdf5name, '/A_det', size(A_det));
h5write(hdf5name, '/A_det', A_det);
h5create(hdf5name, '/cA', size(cA));
h5write(hdf5name, '/cA', cA);
h5create(hdf5name, '/cAg', size(cAg));
h5write(hdf5name, '/cAg', cAg);
h5create(hdf5name, '/cV', size(cV));
h5write(hdf5name, '/cV', cV);
h5create(hdf5name, '/cP', size(cP));
h5write(hdf5name, '/cP', cP);
h5create(hdf5name, '/cW', size(cW));
h5write(hdf5name, '/cW', cW);
h5create(hdf5name, '/cWtot', size(cWtot));
h5write(hdf5name, '/cWtot', cWtot);
h5create(hdf5name, '/cRPY', size(cRPY));
h5write(hdf5name, '/cRPY', cRPY);
h5create(hdf5name, '/RFx', size(RFx_array));
h5write(hdf5name, '/RFx', RFx_array);
h5create(hdf5name, '/RFy', size(RFy_array));
h5write(hdf5name, '/RFy', RFy_array);
%
dlmwrite(strcat(target_folder, 'rng.txt'), rng_seed, 'precision', '%u');
%%
hdf5name = strcat(target_folder, now_string, '_data.hdf5');
for i = 1:size(data_table, 1)
    for j = 1:size(data_table, 2)
        cell_name = strcat('/', point_names(i), '-', param_set{j}(1), '-', param_set{j}(2:end));
        if size(data_table{i, j}, 2) > 0
            h5create(hdf5name, cell_name{1}, size(data_table{i, j}));
            h5write(hdf5name, cell_name{1}, data_table{i, j});
        end
    end
end
%%
if length(strsplit(xml_file, filesep)) == 1
    path = strsplit(xml_file, '/');
    scenario_copy = strcat(target_folder, path{end});
else
    path = strsplit(xml_file, filesep);
    scenario_copy = strcat(target_folder, path{end});
end
copyfile(xml_file, scenario_copy);
%%
save(mat_name);



%% Файл с параметрами реального набора датчиков,
% в соотв. с присланным описанием.
%
quat_path = 'quat_rot_tst/';
xml_func_path = 'xml_io_tools/';
movement_set_paths;
%
% Путь к функциям фращения вектора через кватернион
addpath(quat_path);
% Путь к функциям чтения XML
addpath(xml_func_path);
% Чтение параметров из файла:
params = xml_read(xml_file);
%
%% Параметры генерирования траектории с маневрами
% используются в функции route_gen.m
% 
% n_lim = [params.n_lim.min params.n_lim.max];%[2 2];% Число участков в ломаной
v_lim = [params.v_lim.min params.v_lim.max]; % Скорость корабля - от 10 до 23 узлов
r_lim = [params.r_lim.min params.r_lim.max]; % радиус поворота в метрах
t_lim = [params.t_lim.min params.t_lim.max]; % Длительность каждого прямолинейного участка в ломаной траектории, с
flagAccel = params.init_acc;
Puniform = params.acc_prob;
% save('route_gen_params.mat', 'n_lim', 'r_lim', 't_lim', 'quat_path');
%
%%
%
% Случайная страектория или фиксированная:
seed = params.seed;
if seed == 0
    rng('shuffle');
else
    rng(seed);    
end
trace_gen_rng = rng;
rng_seed = trace_gen_rng.Seed;
% Направление прямолинейного движения и скорость:
if isnan(params.course)
    course = randsample(359, 1); % курс, градусов
else
    course = params.course;
end
%
speed = rand * (v_lim(2) - v_lim(1)) + v_lim(1);
%
q0 = w2quat([0 0 deg2rad(course)]');
% Плечо начальногоприложения силы с учетом начального направления (курса) -
% поскольку точка приложения должна лежать в диаметральной плоскости
% корабля. 
RFX = vrq([1 0 0]', q0);
RFY = vrq([0 1 0]', q0);
g0 = 9.81;
g = vrq([0 0 g0]', q0);
%
V0 = speed * 1852 / 3600; % Скорость в м/с
%
% Теперь начальные значения в векторной форме:
cV0 = vrq([V0 0 0]', q0); % начальная линейная скорость центра масс объекта, м/с
cP0 = [0 0 0]'; % начальные координаты центра масс объекта, м
cW0 = [0 0 0]'; % начальная угловая скорость вращения объекта, рад/с
cU0 = [0 0 deg2rad(course)]'; % начальное угловое положение объекта, рад
%
%% География
%
% Координаты исходные (минск, победителей 127). Высота - от балды
location0 = [params.location.latitude, params.location.longitude, params.location.height];
% location0 = [53.939156, 27.466900, 180];
wgs = referenceEllipsoid(params.ell);
%
%% Параметры датчиков:
%
% Вызов отдельного файла, где прописаны все датчики:
[sensors, userpoints] = sensors_setup_func(params);
%
num_pts = length(sensors);
param_set = {'ax', 'ay', 'az', 'wx', 'wy', 'wz', 'ux', 'uy', 'uz', 'gx', 'gy', 'gz', 'vx', 'vy', 'vz'};
axis_num = [1 2 3 1 2 3 1 2 3 1 2 3 1 2 3];
data_table = cell([num_pts, length(param_set)]);
get_param_idx = @(x)find(strcmp(param_set, x));
%
point_set0 = zeros(3, num_pts);
point_names = cell(num_pts, 1);
dt = Inf;  % Длительность системного дискрета времени. 
% Определяем как минимальный из всех датчиков
for i = 1:num_pts
    point_set0(:, i) = sensors{i}.xyz;
    point_names{i} = sensors{i}.name;
    if sensors{i}.dt < dt
        dt = sensors{i}.dt;
    end
end
shoulder_coeff = 1;
% !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
% set_random_imu_pos3;% !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
% disp('!!! RANDOM IMU positions !!!');% !!!!!!!!!!!!!!!
% !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
%
Tmod = params.Tmod; % Длительность моделирования в часах
mod_size = floor(Tmod * 3600 / dt) + 1;
%
% Поворот точек в направлении начального азимута:
point_set = zeros(size(point_set0));
for i = 1:num_pts
    point_set(:, i) = vrq(point_set0(:, i), q0);
end
%
%%
% user_point_set = zeros(5, length(userpoints));
% for i = 1:length(userpoints)
%     user_point_set(1:3, i) = userpoints{i}.xyz;
%     user_point_set(4, i) = userpoints{i}.dt;
%     user_point_set(5, i) = userpoints{i}.tshift;
% end

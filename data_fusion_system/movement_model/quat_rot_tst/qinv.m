function qin = qinv(q)
% Inversion of quaternion
if isa(q, 'quaternion')
    [qw, qx, qy, qz] = parts(q);
else
    qw = q(1);
    qx = q(2);
    qy = q(3);
    qz = q(4);
end
qi = [qw -qx -qy -qz]';
qin = qnorm(qi);
end
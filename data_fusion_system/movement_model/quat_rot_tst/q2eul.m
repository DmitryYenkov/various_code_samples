function [r, p, y] = q2eul(q)
% Quaternion to euler angles
qw = q(1);
qx = q(2);
qy = q(3);
qz = q(4);
r = atan2(2 * (qw * qx + qy * qz), 1 - 2 * (qx^2 + qy^2));
p = asin(2 * (qw * qy - qx * qz));
y = atan2(2 * (qw * qz + qx * qy), 1 - 2 * (qy^2 + qz^2));
end
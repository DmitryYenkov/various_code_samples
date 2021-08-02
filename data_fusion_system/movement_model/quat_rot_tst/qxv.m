function qv = qxv(q, v)
% Multiply vector with quaternion
if isa(q, 'quaternion')
    [aw,ax,ay,az] = parts(q);
else
    aw = q(1);
    ax = q(2);
    ay = q(3);
    az = q(4);
end
bx = v(1);
by = v(2);
bz = v(3);
qw = - ax * bx - ay * by - az * bz;
qx = aw * bx + ay * bz - az * by;
qy = aw * by - ax * bz + az * bx;
qz = aw * bz + ax * by - ay * bx;
if isa(q, 'quaternion')
    qv = quaternion([qw,qx,qy,qz]);
else
    qv = [qw qx qy qz]';
end
end
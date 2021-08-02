function qq = qxq(q1, q2)
% Multiply two quaternions
if isa(q1, 'quaternion')
    [aw,ax,ay,az] = parts(q1);
else
    aw = q1(1);
    ax = q1(2);
    ay = q1(3);
    az = q1(4);
end
if isa(q2, 'quaternion')
    [bw,bx,by,bz] = parts(q2);
else
    bw = q2(1);
    bx = q2(2);
    by = q2(3);
    bz = q2(4);
end
qw = aw * bw - ax * bx - ay * by - az * bz;
qx = aw * bx + ax * bw + ay * bz - az * by;
qy = aw * by - ax * bz + ay * bw + az * bx;
qz = aw * bz + ax * by - ay * bx + az * bw;
if isa(q1, 'quaternion') || isa(q2, 'quaternion')
    qq = quaternion([qw,qx,qy,qz]);
else
    qq = [qw qx qy qz]';
end
end
function qn = qnorm(q)
% Normalization of quaternion
if isa(q, 'quaternion')
    [qw, qx, qy, qz] = parts(q);
else
    qw = q(1);
    qx = q(2);
    qy = q(3);
    qz = q(4);
end
qn = quaternion([qw qx qy qz] / norm([qw qx qy qz]));
[qw, qx, qy, qz] = parts(qn);
qn = [qw qx qy qz]';
end
function vr = vrq(v, q)
% Rotate vector by quaternion
% taken from here:
% https://www.pvsm.ru/matematika/88039
%
if ~isa(q, 'quaternion')
    q_ = quaternion(q(1), q(2), q(3), q(4));
else
    q_ = q;
end
qv = qxv(q_, v);
qq = qxq(qv, qinv(q_));
[~,qx,qy,qz] = parts(qq);
vr = [qx qy qz]';
if any(isnan(q))
    vr = v;
end
end%function

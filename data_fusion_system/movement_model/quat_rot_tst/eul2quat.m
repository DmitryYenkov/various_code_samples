function q = eul2quat(r, p, y)
% get quaternion from roll-pitch-yaw angles (in rad)
% taken from here: 
% https://www.euclideanspace.com/maths/geometry/rotations/conversions/eulerToQuaternion/index.htm
% (alternative form equations)
%
c1 = cos(r);
c2 = cos(p);
c3 = cos(y);
s1 = sin(r);
s2 = sin(p);
s3 = sin(y);
%
w = sqrt(1.0 + c2 * c3 + c2*c1 - s2 * s3 * s1 + c3*c1) / 2;
x = (c3 * s1 + c2 * s1 + s2 * s3 * c1) / (4.0 * w);
y = (s2 * c3 + s2 * c1 + c2 * s3 * s1) / (4.0 * w);
z = (-s2 * s1 + c2 * s3 * c1 + s3) / (4.0 * w);
%
q = [w x y z]';
end%function
function w = quat2w(q)
    if q(1) == 1
        w = [0 0 0]';
    else
        a = acos(q(1));
        w = 2 * a * q(2:4) / sin(a);
    end
end
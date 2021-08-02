function q = w2quat(w)
    n = norm(w);
    if n == 0
        q = [1 0 0 0]';
    else
        q = [cos(n/2); sin(n/2) * w / n];
    end
end
function q = av2quat(a, v)
    n = norm(v);
    q = [cos(a/2); sin(a/2) * v / n];
end
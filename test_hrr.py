import numpy as np

def bind(v1, v2):
    return np.fft.ifft(np.fft.fft(v1) * np.fft.fft(v2)).real

def unbind(bound_v, v1):
    return np.fft.ifft(np.fft.fft(bound_v) * np.conj(np.fft.fft(v1))).real

def cosine_sim(v1, v2):
    return np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2) + 1e-9)

dim = 1024
v1 = np.random.randn(dim)
v1 /= np.linalg.norm(v1)
v2 = np.random.randn(dim)
v2 /= np.linalg.norm(v2)

bv = bind(v1, v2)
rv2 = unbind(bv, v1)

print(f"Random Vector Sim: {cosine_sim(rv2, v2)}")

import numpy as np

def bind(v1, v2):
    return np.fft.ifft(np.fft.fft(v1) * np.fft.fft(v2))

def unbind(bound_v, v1):
    # For unitary HRR, unbinding is circular correlation (involution)
    # v2 ~ bound_v * inv(v1)
    # inv(v1) in frequency domain is conj(fft(v1))
    return np.fft.ifft(np.fft.fft(bound_v) * np.conj(np.fft.fft(v1)))

def cosine_sim(v1, v2):
    v1 = np.real(v1)
    v2 = np.real(v2)
    return np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2) + 1e-9)

dim = 1024
# Standard HRR usually uses normal distribution for components
v1 = np.random.normal(0, 1/np.sqrt(dim), dim)
v2 = np.random.normal(0, 1/np.sqrt(dim), dim)

bv = bind(v1, v2)
rv2 = unbind(bv, v1)

print(f"Normal Distribution Sim: {cosine_sim(rv2, v2)}")

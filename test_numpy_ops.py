import numpy as np
import time

dim = 4096
n = 10000

a = np.random.randn(dim)
b = np.random.randn(dim)

# Normal multiplication vs circular convolution logic
def conv_logic(a, b):
    fa = np.fft.rfft(a)
    fb = np.fft.rfft(b)
    return np.fft.irfft(fa * fb, n=len(a))

start = time.time()
for _ in range(n):
    conv_logic(a, b)
end = time.time()
print(f"FFT time: {end - start:.4f}s")

# Vectorized harvesting check
objs = [np.random.randn(dim) for _ in range(100)]
start = time.time()
for obj in objs:
    fa = np.fft.rfft(obj)
end = time.time()
print(f"Serial FFT: {end - start:.4f}s")

objs_matrix = np.array(objs)
start = time.time()
fa_matrix = np.fft.rfft(objs_matrix, axis=1)
end = time.time()
print(f"Vectorized FFT: {end - start:.4f}s")

import numpy as np
import time

dim = 4096
a = np.random.randn(dim)
b = np.random.randn(dim)

def bind_fft(a, b):
    return np.fft.ifft(np.fft.fft(a) * np.fft.fft(b)).real

def bind_rfft(a, b):
    return np.fft.irfft(np.fft.rfft(a) * np.fft.rfft(b), n=len(a))

# Test correctness
res_fft = bind_fft(a, b)
res_rfft = bind_rfft(a, b)
print(f"Correctness check: {np.allclose(res_fft, res_rfft)}")

# Benchmark
n = 10000
start = time.time()
for _ in range(n):
    bind_fft(a, b)
end = time.time()
print(f"FFT time: {end - start:.4f}s")

start = time.time()
for _ in range(n):
    bind_rfft(a, b)
end = time.time()
print(f"RFFT time: {end - start:.4f}s")

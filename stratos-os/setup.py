from setuptools import setup, find_packages

setup(
    name='stratos-os',
    version='1.0.0',
    description='Fiber-Stratified Optimization (FSO) Manifold Runtime',
    long_description='A decentralized, topological execution environment that bypasses local OS storage by compiling logic dynamically from a mathematical Torus.',
    author='FSO Architecture Group',
    packages=find_packages(),
    install_requires=[
        'numpy>=1.20.0',
        'scikit-learn>=1.0' # For Semantic Router capabilities
    ],
    classifiers=[
        'Intended Audience :: Developers',
        'Intended Audience :: Science/Research',
        'Programming Language :: Python :: 3',
        'Topic :: Scientific/Engineering :: Artificial Intelligence',
    ],
)

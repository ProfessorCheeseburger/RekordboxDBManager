from setuptools import setup, find_packages

setup(
    name='dj_tagtool',
    version='0.1.0',
    author='Your Name',
    author_email='your.email@example.com',
    description='A music tagging tool for DJs',
    packages=find_packages(),  # Automatically find all packages in dj_tagtool folder
    install_requires=[
        'mutagen',   # your external dependency
        # add more here if you add more external libs
    ],
    entry_points={
        'console_scripts': [
            'dj_tagtool = dj_tagtool.main:main',  # assuming you create a main() function in main.py
        ],
    },
    python_requires='>=3.7',
    classifiers=[
        'Programming Language :: Python :: 3',
        'Operating System :: OS Independent',
    ],
)

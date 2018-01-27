from setuptools import setup

def readme():
    with open('README.md') as f:
        return f.read()

setup(name='Pi',
      version='0.0.1',
      description='Pi for SCC331 Smart Enviroment Toolkit',
      long_description=readme(),
      classifiers=[
        'Development Status :: 3 - Alpha',
        'License :: MIT License',
        'Programming Language :: Python :: 2.7',
      ],
      keywords='funniest joke comedy flying circus',
      url='http://github.com/SCC331Penguins/Pi',
      license='MIT',
      install_requires=[
          'markdown',
      ],
      include_package_data=True,
      zip_safe=False)

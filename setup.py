import os
import setuptools
import siswrapper._version as _version

version_date = _version.__version__
version = version_date.split(" ")[1]


def get_readme():
    """
    Returns README.md content.
    :return str long_description: README.md content
    """
    long_description = ""
    this_directory = os.path.abspath(os.path.dirname(__file__))

    if os.path.isfile(os.path.join(this_directory, 'README.md')):
        with open(os.path.join(this_directory, 'README.md'), encoding='utf-8') as f:
            long_description = f.read()
    else:
        raise Exception("README.md file not found")

    return long_description


if __name__ == '__main__':

    setuptools.setup(
        install_requires=['pexpect==4.8.0'],  # dependency
        python_requires='>=3',
        packages=setuptools.find_packages(include=['siswrapper']),

        name='siswrapper',  # name of the PyPI-package.
        version=version,    # version number
        author="Zenaro Stefano (mario33881)",
        author_email="mariortgasd@hotmail.com",
        url="https://github.com/mario33881/siswrapper",
        keywords='SIS BLIF siswrapper wrapper development',
        license='MIT',
        description='A Python wrapper for SIS',
        long_description=get_readme(),
        long_description_content_type='text/markdown',
        classifiers=[
            # How mature is this project? Common values are
            #   3 - Alpha
            #   4 - Beta
            #   5 - Production/Stable
            'Development Status :: 5 - Production/Stable',

            # Indicate who your project is intended for
            'Intended Audience :: Developers',
            'Topic :: Software Development',
            'Topic :: Software Development :: Libraries :: Python Modules',

            # Pick your license as you wish (should match "license" above)
            'License :: OSI Approved :: MIT License',

            # Specify the Python versions you support here. In particular, ensure
            # that you indicate whether you support Python 2, Python 3 or both.
            'Programming Language :: Python :: 3',

            # Operating systems
            'Operating System :: Unix',
        ]
    )

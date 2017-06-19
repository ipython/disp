from setuptools import setup

description='Providing default representations of common objects in Python land',

try:
    import pypandoc
    description = pypandoc.convert(open('README.md','r').read(), format='markdown', to='rst')
except:
    print('Issues running or importing pypandoc. If you are publishing the package the description will be missing.')

setup(name='disp',
      version='0.0.3',
      description='Providing default representations of common objects in Python land',
      url='http://github.com/ipython/disp',
      author='IPython developers',
      author_email='ipython-dev@python.org',
      license='BSD',
      packages=['disp'],
      zip_safe=False)

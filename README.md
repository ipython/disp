# Disp

Providing default representations of common objects in Python land

![pretty-spark-context](./pretty-context.png)

Works in IPython when the object is the value returned by the last statement of
a cell, or when calling `display()` on it. 

## Install 

```
$ pip install disp
$ ipython -c 'import disp; disp.install()'
💖 Installation succeeded: enjoy disp ! 💖
```

## Uninstall

```
$ ipython -c 'import disp; disp.uninstall()'
```

## Supported objects

The following objects will gain superpowers automatically:

 - `pyspark.context:SparkContext`
 - `pyspark.sql:SparkSession`

The followings objects need to be explicitly register with
`disp.activate_builtins()` and will work only on Python 3.6 and later:

 - types
 - functions methods (and alike)
 - modules

The following objects need to be explicitly activated individually for each
type with `disp.activate_for(instance)`:
 
 - requests.models.Response (Python 3.6+ only)

A couple of other objects are secretly available on Python 3.6, but are still
unstable so-far (dig through the source).

## Example

See our [example notebook](http://nbviewer.jupyter.org/github/ipython/disp/blob/master/example/Disp-Example-builtins.ipynb)

## Do you support more objects? 

Do you want to submit a Pull Request? We'll probably accept it. 🤓

# releasing

Bump version number in `setup.py`.
Install `twine`

```
$ python setup.py sdist bdist_wheel
$ twine upload dist/*
```

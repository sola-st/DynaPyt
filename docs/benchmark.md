For all projects first:
```
pip install pytest pytest-xdist
```
Pandas:
```
pip install numpy pytz Cython hypothesis
python setup.py install
bash test_fast.sh
```
Django:
```
pip install .
pip install -r tests/requirements./py3.txt
pytest
```
Keras:
```
pip install -r requirements.txt
cd keras
python runall_tests.py
```
Requests:
```
pytest
```
Rich:
```
pip install pygments commonmark
pytest
```
Scikit-learn:
```
pip install -r requirements.txt
python setup.py install
pytest --showlocals -v sklearn --durations=20
```
Scrapy:
```
pip install twisted lxml parsel w3lib cryptography itemadapter pydispatch pyOpenSSL protego
pip install -r tests/requirements.txt
pytest
```
Thefuck:
```
pip install -r requirements.txt
python setup.py install
pytest
```

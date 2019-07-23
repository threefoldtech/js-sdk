# js-ng

next generation of jumpscale

- clone repo
- `cd reparo/js-ng`


## core
- config: single entry point for configuration retrieval/update
- exceptions: unified exception
- logging : unified logging 

## sals
provide abstraction over the system (files, processes, hostfile, ...)

## clients
provide the DSL around popular python packages/ or inhouse clients that mainly communicates with some sort of servers


### ipython

```python
In [1]: from jumpscale.god import j                        
In [2]: g = j.clients.github.Github("first")               
In [3]: g.config.data                                      
Out[3]: {'user': 'ahmed2', '__tok': 'abcedf'}
In [4]: g.config.data = {'user':'tftech', '__tok':'newpass'}                                                  

In [5]: g.config.data              
Out[5]: {'user': 'tftech', '__tok': 'newpass'}                        
```
# taskpl

task pipeline for human

## what is `taskpl`?

taskpl is a task management project, which based on file management.

## how to use it?

### init a declarative pipeline

```python
[config]
name = "testonly"


[pipeline]

  [pipeline.stage1]
  desc = ""
    
    [pipeline.stage1.substage1]
    desc = "blablabla"

    [pipeline.stage1.substage2]
    desc = ""
    
        [pipeline.stage1.substage2.subsubstage1]
        desc = ""


  [pipeline.stage2]
  desc = ""
```

### and, build a job on the top of pipeline

pipeline is the prototype of job.

![create_job.png](https://i.loli.net/2020/03/17/paho8UYiATEfxLI.png)

if I name it `1`, I will get a directory tree which same as my pipeline.

![filemanage.png](https://i.loli.net/2020/03/17/pOe5RlgQsoGWwhn.png)

when I upload files (task result), status will be updated immediately. for example, I upload a file to substage2:

![tree.png](https://i.loli.net/2020/03/17/gJsP4DKSVB9n5Wc.png)

## dependencies

> filebrowser has been archived. But v2.0.12 is nearly stable now. Of course you can use something else you like to replace it.

- [filebrowser](https://github.com/filebrowser/filebrowser)
- [taskpl-dashboard](https://github.com/taskpl/taskpl-dashboard)

## license

[MIT](LICENSE)

### Query Language 

### Dataflow

```prolog
user_input_might_reach_function('any.fully.qualified.name').

% example:
user_input_might_reach_function('sqlalchemy.create_engine.connect.execute').
```
> [!NOTE]
> don't forget the dot `.` at the end of the query

> [!NOTE]
> to simplify queries, there is no need<sup>1</sup> to write `sqlalchemy.create_engine().connect().execute`

---

<sup>1</sup> Unlike [CodeQL][1], where `foo.bar` is different from `foo().bar`

[1]: https://codeql.github.com/

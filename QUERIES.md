### Query Language

#### dataflow:

- `user_input_might_reach_function('any.fully.qualified.name')`
- user_input_might_reach_function('sqlalchemy.create_engine.connect.execute').

> 💡Note: to simplify queries, there is *no need*<sup>1</sup> to write  
> `sqlalchemy.create_engine().connect().execute`

---

<sup>1</sup> This is different from [CodeQL][1], where `foo.bar` is different from `foo().bar`

[1]: https://codeql.github.com/
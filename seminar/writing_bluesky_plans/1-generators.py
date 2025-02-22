def small_ints_func():
    print("running func")
    return [0, 1, 2]


def small_ints_gen():
    print("generator start")
    for num in small_ints_func():
        print(f"generator step {num}")
        yield num
    print("generator end")


def meta_gen():
    yield from small_ints_gen()
    print("between gens")
    yield from small_ints_gen()

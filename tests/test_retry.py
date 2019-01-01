from retry import retry


def test_that_retry_works_on_simple_function():

    @retry(Exception)
    def f():
        return True

    assert f


def test_that_retry_works_on_complex_function():
    class C():
        fail = 2

        @retry(Exception, tries=3)
        def f(self):
            self.fail -= 1
            assert self.fail == 0
            return True

    c = C()
    assert c.f()
    assert c.fail == 0

from behave import when, then, step


class Hello():

    @step('we have behave installed')
    def step_impl_installation(context):
        pass

    @when('we implement a test')
    def step_impl_test(context):
        assert True is not False

    @then('behave will test it for us!')
    def step_impl_verify(context):
        assert context.failed is False

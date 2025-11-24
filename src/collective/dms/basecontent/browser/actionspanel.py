from imio.actionspanel.browser.views import ActionsPanelView


class DmsFileActionsPanelView(ActionsPanelView):

    def __init__(self, context, request):
        super(DmsFileActionsPanelView, self).__init__(context, request)
        self.ACCEPTABLE_ACTIONS = ["edit", "external_edit", "delete", "download"]

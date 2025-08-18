class Scene:
    def __init__(self):
        self.objects = []
        self.current_object = None

    def add_object(self, obj):
        self.objects.append(obj)

    def set_current_object(self, obj):
        self.current_object = obj
        self.add_object(obj)
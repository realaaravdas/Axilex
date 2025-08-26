class Scene:
    def __init__(self):
        self.objects = []
        self.current_object = None

    def add_object(self, obj):
        if obj not in self.objects:
            self.objects.append(obj)

    def remove_object(self, obj):
        if obj in self.objects:
            self.objects.remove(obj)

    def set_current_object(self, obj):
        self.current_object = obj
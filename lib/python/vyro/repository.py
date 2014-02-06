class BaseRepository:
    def __init__(self, path):
        self.path = path

class RootRepository(BaseRepository): pass
class VendorRepository(BaseRepository): pass
class StageRepository(BaseRepository): pass

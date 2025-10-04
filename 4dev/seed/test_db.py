from src.infrastructure.database.collections.sample_collections import SampleCollection
from src.infrastructure.database.models.sample_model import SampleModel
import os



def seed():
    for index in range(5):
        print('Seeding sample {}'.format(index))
        sample = {
            "description": "Sample description {}".format(index)
        }
        sample_model = SampleModel(**sample)
        SampleCollection().insert(sample_model)


if __name__ == '__main__':
    seed()
from mindware.components.models.base_nn import BaseImgClassificationNeuralNetwork
from mindware.components.utils.constants import DENSE, SPARSE, UNSIGNED_DATA, PREDICTIONS


class ResNet110_32Classifier(BaseImgClassificationNeuralNetwork):

    def fit(self, dataset, **kwargs):
        from .nn_utils.resnet_32 import resnet110
        if self.grayscale:
            raise ValueError("Only support RGB inputs!")
        self.model = resnet110(num_classes=len(dataset.train_dataset.classes))
        self.model.to(self.device)
        super().fit(dataset, **kwargs)
        return self

    def set_empty_model(self, config, dataset):
        from .nn_utils.resnet_32 import resnet110
        if self.grayscale:
            raise ValueError("Only support RGB inputs!")
        self.model = resnet110(num_classes=len(dataset.classes))

    @staticmethod
    def get_properties(dataset_properties=None):
        return {'shortname': 'ResNet110_32',
                'name': 'ResNet110_32 Classifier',
                'handles_regression': False,
                'handles_classification': True,
                'handles_multiclass': True,
                'handles_multilabel': False,
                'is_deterministic': False,
                'input': (DENSE, SPARSE, UNSIGNED_DATA),
                'output': (PREDICTIONS,)}

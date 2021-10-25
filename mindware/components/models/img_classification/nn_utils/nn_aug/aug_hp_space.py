from ConfigSpace.configuration_space import ConfigurationSpace
from ConfigSpace.conditions import EqualsCondition
from ConfigSpace.hyperparameters import UniformFloatHyperparameter, \
    UniformIntegerHyperparameter, CategoricalHyperparameter, UnParametrizedHyperparameter
from ConfigSpace.conditions import EqualsCondition

from torchvision.transforms import transforms

from mindware.components.utils.configspace_utils import check_for_bool

resize_size_dict = {'mobilenet': 224,
                    'resnet50': 224,
                    'densenet161': 224,
                    'resnext': 224,
                    'senet': 224,
                    'nasnet': 331,
                    'efficientnet': 224}


def get_aug_hyperparameter_space():
    cs = ConfigurationSpace()
    aug = CategoricalHyperparameter('aug', choices=['True', 'False'], default_value='True')
    auto_aug = CategoricalHyperparameter('auto_aug', choices=['True', 'False'], default_value='False')
    random_flip = CategoricalHyperparameter('random_flip', choices=['True', 'False'], default_value='True')
    affine = CategoricalHyperparameter('affine', choices=['True', 'False'], default_value='True')
    jitter = CategoricalHyperparameter('jitter', choices=['True', 'False'], default_value='True')
    brightness = CategoricalHyperparameter('brightness', choices=[0.2], default_value=0.2)
    saturation = CategoricalHyperparameter('saturation', choices=[0.2], default_value=0.2)
    hue = CategoricalHyperparameter('hue', choices=[0.15], default_value=0.15)
    degree = CategoricalHyperparameter('degree', choices=[10, 20, 30], default_value=10)
    shear = CategoricalHyperparameter('shear', choices=[0.05, 0.1, 0.2], default_value=0.1)

    cs.add_hyperparameters([aug, random_flip, auto_aug, affine, jitter, brightness, saturation, hue, degree, shear])

    auto_aug_on_aug = EqualsCondition(auto_aug, aug, 'True')
    random_flip_on_auto_aug = EqualsCondition(random_flip, auto_aug, 'False')
    affine_on_auto_aug = EqualsCondition(affine, auto_aug, 'False')
    jitter_on_auto_aug = EqualsCondition(jitter, auto_aug, 'False')
    brightness_on_jitter = EqualsCondition(brightness, jitter, 'True')
    saturation_on_jitter = EqualsCondition(saturation, jitter, 'True')
    hue_on_jitter = EqualsCondition(hue, jitter, 'True')
    degree_on_affine = EqualsCondition(degree, affine, 'True')
    shear_on_affine = EqualsCondition(shear, affine, 'True')

    cs.add_conditions([auto_aug_on_aug, random_flip_on_auto_aug, affine_on_auto_aug,
                       jitter_on_auto_aug, brightness_on_jitter, saturation_on_jitter,
                       hue_on_jitter, degree_on_affine, shear_on_affine])

    return cs


def get_transforms(config, image_size=None):
    config = config.get_dictionary()
    if image_size is not None:
        image_size = image_size
    elif config['estimator'] not in resize_size_dict:
        image_size = 32
    else:
        image_size = resize_size_dict[config['estimator']]

    val_transforms = transforms.Compose([
        transforms.Resize(image_size),
        transforms.CenterCrop(image_size),
        transforms.ToTensor(),
    ])
    if check_for_bool(config['aug']):
        if check_for_bool(config['auto_aug']):
            # from .transforms import AutoAugment
            data_transforms = {
                'train': transforms.Compose([
                    # AutoAugment(),
                    transforms.Resize(image_size),
                    transforms.RandomCrop(image_size, padding=int(image_size / 8)),
                    transforms.RandomHorizontalFlip(),
                    transforms.ToTensor(),
                ]),
                'val': val_transforms,
            }
        else:
            transform_list = []
            if check_for_bool(config['jitter']):
                transform_list.append(transforms.ColorJitter(brightness=config['brightness'],
                                                             saturation=config['saturation'],
                                                             hue=config['hue']))
            if check_for_bool(config['affine']):
                transform_list.append(transforms.RandomAffine(degrees=config['degree'],
                                                              shear=config['shear']))

            transform_list.append(transforms.RandomResizedCrop(image_size))
            transform_list.append(transforms.RandomCrop(image_size, padding=4))

            if check_for_bool(config['random_flip']):
                transform_list.append(transforms.RandomHorizontalFlip())

            transform_list.append(transforms.ToTensor())

            data_transforms = {'train': transforms.Compose(transform_list), 'val': val_transforms}
    else:
        data_transforms = {
            'train': transforms.Compose([
                transforms.Resize(image_size),
                transforms.CenterCrop(image_size),
                transforms.ToTensor(),
            ]),
            'val': val_transforms,
        }
    return data_transforms


def get_test_transforms(config, image_size=None):
    if not isinstance(config, dict):
        config = config.get_dictionary().copy()
    else:
        config = config.copy()
    if image_size is not None:
        image_size = image_size
    elif config['estimator'] not in resize_size_dict:
        image_size = 224
    else:
        image_size = resize_size_dict[config['estimator']]
    test_transforms = transforms.Compose([
        transforms.Resize(image_size),
        transforms.CenterCrop(image_size),
        transforms.ToTensor(),
    ])
    return test_transforms

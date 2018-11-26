'''
Utility methods
'''


def get_site_deployment():
    '''
    Get the instance of site deployment
    in an import safe way
    '''
    from deploy import SiteDeploymentSingleton
    return SiteDeploymentSingleton.instance()


def get_game_engine():
    '''
    Get the game engine in an import safe way
    '''
    from jackit2.core.engine import EngineSingleton
    return EngineSingleton.instance()


def get_level_loader():
    '''
    Get the level loader in an import safe way
    '''
    from jackit2.core.loader import LevelLoader
    return LevelLoader.get()


def get_texture_loader():
    '''
    Get the texture loader in an import safe way
    '''
    from jackit2.core.texture import TextureLoader
    return TextureLoader.get()


def get_config():
    '''
    Helper method that returns just the config from
    the site deployment singleton
    '''
    return get_site_deployment().config

from tethys_sdk.base import TethysAppBase, url_map_maker


class LisExplorer(TethysAppBase):
    """
    Tethys app class for LIS Observations Explorer.
    """

    name = 'LIS Observations Explorer'
    index = 'lis_explorer:home'
    icon = 'lis_explorer/images/logo.png'
    package = 'lis_explorer'
    root_url = 'lis-explorer'
    color = '#00a1ff'
    description = 'View LIS Observations'
    tags = 'SERVIR'
    enable_feedback = False
    feedback_emails = []

    def url_maps(self):
        """
        Add controllers
        """
        UrlMap = url_map_maker(self.root_url)

        url_maps = (
            UrlMap(
                name='home',
                url='lis-explorer',
                controller='lis_explorer.controllers.home'
            ),
            UrlMap(name='get-ts',
                   url='lis-explorer/get-ts',
                   controller='lis_explorer.controllers.get_ts'),
            UrlMap(name='upload-shp',
                   url='lis-explorer/upload-shp',
                   controller='lis_explorer.ajax_controllers.upload_shp'),

        )

        return url_maps

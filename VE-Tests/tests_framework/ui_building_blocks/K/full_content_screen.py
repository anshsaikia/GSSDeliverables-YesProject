from tests_framework.ui_building_blocks.KD.full_content_screen import FullContentScreen,SortType

class KfullContentScreen(FullContentScreen):

    def sort(self, sort_type=SortType.A_TO_Z):
        title_menu = self.test.milestones.get_dic_value_by_key('DIC_SORT_SORT', 'general')
        self.select_menu_item(title_menu)
        if sort_type == SortType.A_TO_Z:
            title_menu = self.test.milestones.get_dic_value_by_key('DIC_SORT_BY_TITLE', 'general')
        elif sort_type == SortType.DATE:
            title_menu = self.test.milestones.get_dic_value_by_key('DIC_SORT_BY_DATE', 'general')

        self.select_menu_item(title_menu)

import os
import pandas as pd
import numpy as np
from datetime import datetime
import sysconfig
from ipywidgets import Image, HTML, Button, IntProgress, \
    Box, HBox, VBox, GridBox, Layout, ButtonStyle, Output
from IPython.display import display, clear_output


package_dir = sysconfig.get_paths()['purelib']
logo_path = package_dir + '/tortus/Images/tortus_logo.png'

try:
    with open(logo_path, 'rb') as image_file:
        image = image_file.read()

    logo = Image(value=image, format='png', width='100%')
    welcome = HTML("<h2 style='text-align:center'>\
        easy text annotation in a Jupyter Notebook</h2>")

except:
    logo = HTML("<h1 style='text-align:center'>t &nbsp; <span style=\
        'color:#36a849'>o</span> &nbsp; r &nbsp; t &nbsp; u &nbsp; s</h2>")
    welcome = HTML("<h3 style='text-align:center'>\
        easy text annotation in a Jupyter Notebook</h3>")

display(logo, welcome)

class Tortus:
    '''Text annotation within a Jupyter Notebook
    
    :attr annotation_index: A counter for the annotations in progress

    :param df: A dataframe with texts that need to be annotated
    :type df: pandas.core.frame.DataFrame

    :param text: The name of the column containing the text to be annotated
    :type text: str

    :param num_records: Number of records to annotate, defaults to 10
    :type num_records: int, optional
    
    :param id_column: The name of the column containing ID of the text - if None, ``id_column`` 
        is the index of ``df``, default is None
    :type id_column: str, optional

    :param annotations: The dataframe with annotations previously created in this tool.
        If None, ``annotations`` is created with columns ``id_column``, ``text``, ``label``, 
        ``annotated_at``, default is None
    :type annotation_df: pandas.core.frame.DataFrame, optional
    
    :param edit_annotations: Whether to edit existing annotations or start annotating new records     
    :type edit_annotations: bool, optional - default is False
    :param random: Determines if records are loaded randomly or sequentially, default is True
    :type random: bool, optional

    :param labels: Annotation labels, default is ['Positive', 'Negative', 'Neutral']
    :type labels: list, optional
    '''
    annotation_index = 0

    MAX_BUTTONS_IN_ROW = 5
    
    def __init__(self, df, text, num_records=10, id_column=None, annotations=None,edit_annotations=False, get_html=None, random=False,
                labels=['Positve', 'Negative', 'Neutral'], display_confirm=False):
        '''Initializes the Tortus class.           
        '''
        
        self.df = df
        self.text = text
        self.num_records = num_records
        self.id_column = id_column
        if annotations is None:
            if id_column is None:
                self.annotations = pd.DataFrame(columns=['id_column', text, 'label', 'annotated_at'])
            else:
                self.annotations = pd.DataFrame(columns=[id_column, text,'label','annotated_at'])
        else:
            self.annotations = annotations.copy()
        self.edit_annotations = edit_annotations
        self.get_html = get_html if get_html else lambda row: row[self.text]            
        self.random = False if self.edit_annotations else random
        self.labels = labels
        self.display_confirm = display_confirm
        self.subset_df = self.create_subset_df()


    def create_subset_df(self):
        '''
        Subsets ``df`` to include only records cued for annotation.

        If ``annotations`` already exists, those records will excuded from the annotation tool.

        :returns: A dataframe that will be used in the annotation tool.
        :rtype: pandas.core.frame.DataFrame
        '''
        if self.annotations.empty:
            subset_df = self.df.copy()

        else:
            already_annotated = self.annotations[self.text].to_list()
            row_selection_to_annotate = self.df[self.text].isin(already_annotated)
            if not self.edit_annotations:
                row_selection_to_annotate = ~row_selection_to_annotate
            subset_df = self.df[row_selection_to_annotate]

        if self.random:            
            subset_df = subset_df.sample(n=self.num_records)            
        else:            
            subset_df = subset_df[:self.num_records]            

        return subset_df


    def create_record_id(self):
        '''Provides a record id for ``annotations``.

        :returns: A list of record ids that refer to each text in subset df created by 
            :meth:`create_subset_df` method.
        :rtype: list
        '''
        if self.id_column is None:
            record_id = self.subset_df.index.to_list()
        else:
            record_id = self.subset_df[self.id_column].to_list()
        return record_id

    def make_html(self, row):
        '''Changes text to html for annotation widget user interface.

        :param text: Text for conversion to html.
        :type text: str

        :returns: HTML snippet
        :rtype: str
        '''
        html = '<h4>' + self.get_html(row) + '</h4>'
        return html

    def get_annotation_row_from_subset_iloc(self,subset_iloc):
        cur_row = self.subset_df.iloc[subset_iloc]
        row_annot = self.annotations[self.annotations[self.id_column] == cur_row[self.id_column]]
        return row_annot.iloc[0] if row_annot.shape[0] > 0 else None
    
    def annotate(self):
        '''Displays texts to be annotated in a UI. Loads user inputted labels and timestamps into
            ``annotations`` dataframe.
        '''
        try:
            with open(logo_path, 'rb') as image_file:
                image = image_file.read()
                logo = Image(value=image, format='png', width='40%')

        except:
            logo = HTML('<h1>t &nbsp; <span style="color:#36a849">o</span> \
            &nbsp; r &nbsp; t &nbsp; u &nbsp; s</h1>')

        rules = HTML(
            'Click on the label corresponding with the text below. Each selection requires \
                confirmation before proceeding to the next item.')        
        html = self.make_html(self.subset_df.iloc[self.annotation_index])
        text = HTML(html)
# TODO:Debug:Remove
#        print('annotation_index=',self.annotation_index)
#        print('annotations',self.annotations[['index','NERed_par','label']])
        # If there is an label for this row, color the label button (see button_color, below)
        row_annot = self.get_annotation_row_from_subset_iloc(self.annotation_index)        
        annot_label = None
        if row_annot is not None:        
            annot_label = row_annot.label
            
        labels = []
        for label in self.labels:
            label_button = Button(
                description=label,
                layout=Layout(border='solid', flex='1 1 auto', width='auto'),
                style=ButtonStyle(button_color='#eeeeee', font_weight='bold'))                        
            if label.lower() == annot_label:                
                label_button.style.button_color = '#36a849'
                
                
            labels.append(label_button)

        label_buttons = HBox(labels)
        
        skip_button = Button(
            description='Skip',
            layout=Layout(border='solid', flex='1 1 auto', width='auto'),
            style=ButtonStyle(button_color='#eeeeee', font_weight='bold'))
       
        confirm_button = Button(
            description='Confirm selection',
            layout=Layout(border='solid', flex='1 1 auto', width='auto', grid_area='confirm'),
            style=ButtonStyle(button_color='#eeeeee', font_weight='bold'))
        
        prev_button = Button(
            description='Prev',
            layout=Layout(border='solid', flex='1 1 auto', width='auto', grid_area='prev'),
            style=ButtonStyle(button_color='#eeeeee', font_weight='bold'))
        
        
        redo_button = Button(
            description='Try again',
            layout=Layout(border='solid', flex='1 1 auto', width='auto', grid_area='redo'),
            style=ButtonStyle(button_color='#eeeeee', font_weight='bold'))
        
        progress_bar = IntProgress(
                value=self.annotation_index,
                min=0,
                max=self.num_records,
                step=1,
                description=f'{self.annotation_index + 1}/{self.num_records}',
                bar_style='',
                orientation='horizontal',
                layout=Layout(width='50%', align_self='flex-end'))
        progress_bar.style.bar_color = '#36a849'
    
        header = HBox([logo, progress_bar])
        sentiment_buttons = HBox([label_buttons, skip_button,prev_button])
        sentiment = labels + [skip_button,prev_button]
        confirm = [confirm_button, redo_button]

        box_layout = Layout(
            display='flex',
            flex_flow='row',
            align_items='stretch',
            width='100%'
        )

        btn_chunks = np.array_split(sentiment,len(sentiment) // self.MAX_BUTTONS_IN_ROW)
        box_sentiment = VBox([HBox(list(chunk)) for chunk in btn_chunks])
        box_confirm = Box(confirm, layout=box_layout)

        all_buttons = VBox(
            [box_sentiment, box_confirm],
            layout=Layout(width='auto', grid_area='all_buttons')
        )

        ui = GridBox(
            children=[all_buttons],
            layout=Layout(
                width='100%',
                grid_template_rows='auto auto',
                grid_template_columns='15% 70% 15%',
                grid_template_areas='''
                ". all_buttons ."
                ''')
        )
        
        output = Output()

        display(header, rules, text, ui, output)
        confirm_button.layout.visibility = 'hidden'
        redo_button.layout.visibility = 'hidden'    


        def label_or_skip_buttons_clicked(button,skip=False):
            '''Response to button click of any label or skip buttons.
            
            Appends/Updates ``annotations`` with label selection.
            :param button: Label/skip buttons click. 
            :param skip: True if skip buttons click, false if any of the labels
            '''
            button.style.button_color = '#36a849'
            record_id = self.create_record_id()
            row_annot = self.get_annotation_row_from_subset_iloc(self.annotation_index)            
            new_button_label = str(button.description).lower()
            if row_annot is not None:                
                idx = row_annot.name 
                lbl = row_annot.label if skip else new_button_label
            else: 
                idx = len(self.annotations)
                lbl = None if skip else new_button_label
                
            self.annotations.loc[idx] = [
                record_id[self.annotation_index],
                self.subset_df[self.text].iloc[self.annotation_index],
                lbl,
                datetime.now().replace(microsecond=0)  
            ]
            
            for label in labels:
                label.disabled = True
                if button != label:
                    label.layout.border = 'None'

            skip_button.disabled = True
            if not skip:
                skip_button.layout.border = 'None'
                
            with output:
                clear_output(True)                
                if self.display_confirm:
                    sentiment_buttons.layout.visibility = 'visible'                
                    confirm_button.layout.visibility = 'visible'
                    redo_button.layout.visibility = 'visible'
                
            if not self.display_confirm:    
                confirm_button_clicked(None)
                
        def label_buttons_clicked(button):
            label_or_skip_buttons_clicked(button,skip=False)
                
        for label in labels:
            label.on_click(label_buttons_clicked)
        

        def skip_button_clicked(button):
            '''Response to button click of the skip button.

            Appends ``annotations``. Label value is ``Null``.
            
            :param button: Skip button click.
            '''
            label_or_skip_buttons_clicked(button,skip=True)                        
                
        skip_button.on_click(skip_button_clicked)


        def move_clicked(delta):
            '''Response to click of the confirm button.

            Advances the ``annotation_index`` to view the next/prev item in the annotation tool.
                Indicates the tool is done if ``annotation_index`` does not advance further.
                
            
            :param button: Confirmation button click.
            '''
            if delta == -1 and self.annotation_index == 0:
                return
            
            if self.annotation_index < len(self.subset_df) - 1:
                self.annotation_index += delta
                clear_output(True)
                self.annotate()
            else:

                clear_output(True)
                progress_bar.value = self.num_records
                progress_bar.description = 'Complete' if delta == 1 else 'Start'
                display(header, output)    

        def confirm_button_clicked(button):
            move_clicked(1)
        
        confirm_button.on_click(confirm_button_clicked)
        
        def prev_button_clicked(button):
            move_clicked(-1)
            
        prev_button.on_click(prev_button_clicked)


        def redo_button_clicked(button):
            '''Response to click of the redo button.

            Deletes the most recent input to ``annotations``.
            
            :param button: Redo button click.
            '''
            self.annotations = self.annotations.head(-1)
            for label in labels:
                label.style.button_color = '#eeeeee'
                label.disabled = False
                label.layout.border = 'solid'
                
            skip_button.style.button_color = '#eeeeee'
            skip_button.disabled = False
            skip_button.layout.border = 'solid'

            with output:
                clear_output(True)
                sentiment_buttons.layout.visibility = 'visible'
                confirm_button.layout.visibility = 'hidden'
                redo_button.layout.visibility = 'hidden'

        redo_button.on_click(redo_button_clicked)


def get_annotated_path(data_path):
    arr = os.path.splitext(data_path)
    return arr[0] + '_annotated' + arr[1]

def load_annotated_data(data_path):
    """
    data_path : path to .csv original df, path/data.csv --> where it may contain path/data_annotated.csv
        
    df_data : dataframe with labels, to pass to tortus ctor to continue annotations from a checkpoint    
    """    
    ann_data_path = get_annotated_path(data_path)
    df_data = None
    if os.path.isfile(ann_data_path):
        df_data = pd.read_csv(ann_data_path)
    return df_data



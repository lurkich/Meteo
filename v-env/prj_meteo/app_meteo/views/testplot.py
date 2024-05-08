from django.views.generic import TemplateView
from chartjs.views.lines import BaseLineChartView


class LineChartJSONView(BaseLineChartView):


    def get_labels(self):
        """Return 7 labels for the x-axis."""
        return ["08", "09", "10", "11", "12", "13", "14", "15", "16", "17", "18", "19", "20", "21", "22", "23", "24", "01", "02", "03", "04", "05", "06", "07"]

    def get_providers(self):
        """Return names of datasets."""
        # return ["temperature", "pluie"]
        return ["temperature"]

    def get_data(self):
        """Return 3 datasets to plot."""

        # return [[75, 44, 92, 11, 44, 95, 35,6,7,8,9,10,11,12,20,25,14,16,12, 5,8,9,14,9],
        #         [10, 0, 50, 100, 5,0,0,5,6,9,10,45,78,20,65,2,0,0,0,14,9,65,80,32]]


        return [[-15, -10, 2, 11, 31, 25, -5,6,7,8,9,10,11,12,20,25,14,16,12, 5,8,9,14,9]]




line_chart = TemplateView.as_view(template_name='testplot.html')
line_chart_json = LineChartJSONView.as_view()
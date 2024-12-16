import typing
from tkinter import *
from tkinter.messagebox import *
from tkinter.ttk import *

import acribis_scores.abc_af_bleeding as abc_af_bleeding
import acribis_scores.abc_af_death as abc_af_death
import acribis_scores.abc_af_stroke as abc_af_stroke
import acribis_scores.barcelona_hf_v3 as barcelona_hf_v3
import acribis_scores.chads_vasc as chads_vasc
import acribis_scores.charge_af as charge_af
import acribis_scores.has_bled as has_bled
import acribis_scores.maggic as maggic
import acribis_scores.smart as smart
import acribis_scores.smart_reach as smart_reach

SCORES = {'CHA2DS2-VASc': (chads_vasc.Parameters, chads_vasc.calc_chads_vasc_score),
          'HAS-BLED': (has_bled.Parameters, has_bled.calc_has_bled_score),
          'SMART': (smart.Parameters, smart.calc_smart_score),
          'SMARTReach': (smart_reach.Parameters, smart_reach.calc_smart_reach_score),
          'CHARGE-AF': (charge_af.Parameters, charge_af.calc_charge_af_score),
          'MAGGIC': (maggic.Parameters, maggic.calc_maggic_score),
          'BARCELONA Bio-HF V3': (barcelona_hf_v3.Parameters, barcelona_hf_v3.calc_barcelona_hf_score),
          'ABC-AF Stroke': (abc_af_stroke.Parameters, abc_af_stroke.calc_abc_af_stroke_score),
          'ABC-AF Bleeding': (abc_af_bleeding.Parameters, abc_af_bleeding.calc_abc_af_bleeding_score),
          'ABC-AF Death': (abc_af_death.Parameters, abc_af_death.calc_abc_af_death_score)}


class Calculator(Frame):
    def __init__(self, master: Misc | None = None, padding=10, **kwargs):
        super().__init__(master=master, padding=padding, **kwargs)
        self.winfo_toplevel().title('Calculator')
        self.grid()
        self.__form = None
        self.__fields = None
        self.__parameters = {}
        self.__selected_score = StringVar(self)
        self.__result = StringVar(self, 'Result: ---')
        self.__result_label = Label(self, textvariable=self.__result)
        self.__result_label.grid(column=1, row=2)
        Label(self, text='Selected Score:').grid(column=0, row=0)
        OptionMenu(self, self.__selected_score, next(iter(SCORES)), *SCORES.keys()).grid(column=1, row=0)
        Button(self, text='Calculate', command=self.calc_score).grid(column=1, row=3)
        self.__selected_score.trace('w', self.__update__)
        self.__build_form__()

    def __build_form__(self):
        self.__form = Frame(self)
        self.__form.grid()
        self.__form.grid(column=0, row=1, columnspan=2)
        self.__fields = typing.get_type_hints(SCORES[self.__selected_score.get()][0])
        i = 0
        for parameter, input_type in self.__fields.items():
            Label(self.__form, text=parameter).grid(column=0, row=i)
            if input_type is bool:
                var = BooleanVar(self, False)
                Checkbutton(self.__form, variable=var).grid(column=1, row=i)
            else:
                var = StringVar(self)
                reg = self.register(self.__validate_input__)
                parameter_escaped = parameter.replace('%', '%%')
                Entry(self.__form, textvariable=var, validate='key',
                      validatecommand=(reg, parameter_escaped, '%P')).grid(column=1, row=i)
            self.__parameters[parameter] = var
            i += 1

    def __validate_input__(self, parameter, value):
        if not value:
            return True
        try:
            self.__fields[parameter](value)
            return True
        except ValueError:
            self.bell()
            return False

    def __update__(self, *_):
        self.__form.destroy()
        self.__parameters.clear()
        self.__build_form__()
        self.__result.set('Result: ---')

    def calc_score(self):
        score_parameters = {}
        score = None
        for name, value in self.__parameters.items():
            if (type(value) is BooleanVar) or value.get():
                score_parameters[name] = self.__fields[name](value.get())
            else:
                hint = typing.get_type_hints(SCORES[self.__selected_score.get()][0], include_extras=True)[name]
                if typing.get_origin(hint) is not typing.NotRequired:
                    showerror(title='Missing Values!', message=f"{name} is required but not provided as input!")
                    return
        try:
            score = SCORES[self.__selected_score.get()][1](score_parameters)
        except ValueError as e:
            showerror(title='Values Error', message=str(e))
        self.__result.set(f"Result: {score}")
        print(score)


if __name__ == '__main__':
    root = Tk()
    Calculator(root)
    root.mainloop()

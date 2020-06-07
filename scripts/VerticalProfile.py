import numpy as np
import bokeh.plotting as bp
from bokeh.models import CustomJS
from bokeh.layouts import layout, column, row

from bokeh.io import reset_output
from PIL import Image

from bokeh.core.properties import Instance, Float, Array
from bokeh.io import output_file, show, output_notebook
from bokeh.models import ColumnDataSource, Tool
from bokeh.plotting import figure
from bokeh.util.compiler import TypeScript
from bokeh.layouts import layout, column, row


def VerticalProfiler(conn):

    # image vertical profile tool
    TS_CODE = """
    import {GestureTool, GestureToolView} from "models/tools/gestures/gesture_tool"
    import {ColumnDataSource} from "models/sources/column_data_source"
    import {GestureEvent} from "core/ui_events"
    import {View} from "core/view"
    import * as p from "core/properties"

    export class DrawToolView extends GestureToolView {
      model: DrawTool
      inv: number

      constructor(options: View.Options) {
        super(options)
        this.inv = NaN
      }

      invert_vline(x: number) {
        var h = this.model.im_src.data["dh"][0],
            w = this.model.im_src.data["dw"][0],
            im = this.model.im_src.data["image"][0];

        for(var y=0; y<h; y++) im[y*w+x] = 255-im[y*w+x];
      }

      //this is executed when the pan/drag event starts
      _pan_start(_ev: GestureEvent): void {
        this.model.line_src.data = {x: [], y: []}
      }

      //this is executed on subsequent mouse/touch moves
      _pan(ev: GestureEvent): void {
        const {frame} = this.plot_view
        const {sx, sy} = ev
        if (!frame.bbox.contains(sx, sy))
          return

        const x = frame.xscales.default.invert(sx)

        var rx = Math.round(x);

        if(this.inv != rx){
          var res = Array(w),
              w = this.model.im_src.data["dw"][0],
              im = this.model.im_src.data["image"][0]

          if(!isNaN(this.inv)){
            this.invert_vline(this.inv)
          }

          for(var i=0; i<w; i++) res[i] = im[i*w+rx];

          this.model.line_src.data = {
            x: Array(w).fill(0).map(Number.call, Number),
            y: res
          };
          this.model.line_src.change.emit()

          this.invert_vline(rx)
          this.inv = rx
          this.model.im_src.change.emit()
        }
      }

      // this is executed then the pan/drag ends
      _pan_end(_ev: GestureEvent): void {}
    }

    export namespace DrawTool {
      export type Attrs = p.AttrsOf<Props>

      export type Props = GestureTool.Props & {
        im_src: p.Property<ColumnDataSource>,
        line_src: p.Property<ColumnDataSource>
      }
    }

    export interface DrawTool extends DrawTool.Attrs {}

    export class DrawTool extends GestureTool {
      properties: DrawTool.Props

      constructor(attrs?: Partial<DrawTool.Attrs>) {
        super(attrs)
      }

      tool_name = "Drag Span"
      icon = "bk-tool-icon-lasso-select"
      event_type = "pan" as "pan"
      default_order = 12

      static initClass(): void {
        this.prototype.type = "DrawTool"
        this.prototype.default_view = DrawToolView

        this.define<DrawTool.Props>({
          im_src: [ p.Instance ],
          line_src: [ p.Instance ]
        })
      }
    }
    DrawTool.initClass()
    """

    class DrawTool(Tool):
        __implementation__ = TypeScript(TS_CODE)
        im_src = Instance(ColumnDataSource)
        line_src = Instance(ColumnDataSource)
    output_notebook()
    im = Image.open(r'O:\\protons\\Dosimetry_and_QA\\TestData\\LOGOS Example Data\\Bmp Images\\00000001.bmp')
    im_arr = np.array(im)[:,:,0]
    h, w = im_arr.shape

    im_src = ColumnDataSource(data=dict(image=[np.flipud(im_arr)], x=[0], y=[0], dw=[w], dh=[h]))
    line_src = ColumnDataSource(data=dict(x=[], y=[]))

    p1 = figure(plot_width=600, plot_height=200, x_range=(0, w), y_range=(0, h),
                tools=[DrawTool(im_src=im_src, line_src=line_src)])
    p2 = figure(plot_width=600, plot_height=200)

    im = p1.image(image='image', x='x', y='y', dw='dw', dh='dh', source=im_src, palette='Greys256')
    p2.line('x', 'y', source=line_src)

    # bp.show(column(p1, p2))
    layout = column(p1,p2)

    return Panel(child = layout, title = 'VerticalProfiler')

import { PieChart } from '@mui/x-charts/PieChart';
import { colorsArray } from './helper';

export default function PieChartComponent({ item }) {
  const data = Array.isArray(item?.data) ? item.data : [];
  const colors = colorsArray(data.length);

  return (
    <PieChart
      series={[
        {
          innerRadius: 50,
          outerRadius: 100,
          data,
          arcLabel: 'value',
          color: colors,
        }
      ]}
      width={200}
      height={200}
      margin={{ right: 5 }}
      hideLegend={true}
    />
  );
}

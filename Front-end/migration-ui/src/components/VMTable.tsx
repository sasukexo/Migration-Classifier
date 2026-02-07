import type { VM } from "../types/vm";

interface Props {
  data: VM[];
}

export default function VMTable({ data }: Props) {
  return (
    <table border={1} cellPadding={8}>
      <thead>
        <tr>
          <th>VM</th>
          <th>OS</th>
          <th>Decision</th>
          <th>Risk</th>
          <th>Strategy</th>
          <th>Reason</th>
        </tr>
      </thead>

      <tbody>
        {data.map((vm, i) => (
          <tr key={i}>
            <td>{vm["VM Name"]}</td>
            <td>{vm.OS}</td>
            <td>{vm.decision}</td>
            <td>{vm.risk}</td>
            <td>{vm.strategy}</td>
            <td>{vm.reason}</td>
          </tr>
        ))}
      </tbody>
    </table>
  );
}

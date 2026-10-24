import type { BandSummary } from "../../api/types";
import BarGraph from "./BarGraph";

interface BandGraphProps {
  summary: BandSummary;
  highlight: "below_min" | "above_max";
}

const BAND_CATEGORIES = [
  { key: "below_min", label: "Below minimum", color: "#cf1322" },
  { key: "within_band", label: "Within band", color: "#389e0d" },
  { key: "above_max", label: "Above maximum", color: "#d46b08" },
  { key: "no_band", label: "No band", color: "#595959" },
] as const;

export default function BandGraph({ summary, highlight }: BandGraphProps) {
  return (
    <BarGraph
      label={highlight === "below_min" ? "Below-band comparison" : "Above-band comparison"}
      items={BAND_CATEGORIES.map(({ key, label, color }) => ({
        label,
        value: summary[key],
        displayValue: String(summary[key]),
        color: key === highlight ? color : "#bfbfbf",
      }))}
    />
  );
}

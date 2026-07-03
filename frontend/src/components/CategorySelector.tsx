import { JEWELLERY_CATEGORIES, type JewelleryCategory } from "../api/types";

interface CategorySelectorProps {
  value: JewelleryCategory;
  disabled?: boolean;
  onChange: (category: JewelleryCategory) => void;
}

function label(category: JewelleryCategory): string {
  return category.charAt(0).toUpperCase() + category.slice(1);
}

export default function CategorySelector({
  value,
  disabled = false,
  onChange,
}: CategorySelectorProps) {
  return (
    <label className="flex flex-col gap-2">
      <span className="text-sm font-semibold text-slate-700">
        Jewellery type
      </span>
      <select
        value={value}
        disabled={disabled}
        onChange={(event) => onChange(event.target.value as JewelleryCategory)}
        className="w-full rounded-xl border border-slate-200 bg-white px-4 py-3 text-sm font-medium text-slate-700 shadow-sm transition focus:border-indigo-400 focus:outline-none focus:ring-2 focus:ring-indigo-100 disabled:cursor-not-allowed disabled:opacity-60"
      >
        {JEWELLERY_CATEGORIES.map((category) => (
          <option key={category} value={category}>
            {label(category)}
          </option>
        ))}
      </select>
    </label>
  );
}

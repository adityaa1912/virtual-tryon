import { CATALOGUE } from "../data/catalogue";

interface CatalogueGridProps {
  selectedId: string | null;
  disabled?: boolean;
  onSelect: (itemId: string) => void;
}

export default function CatalogueGrid({
  selectedId,
  disabled = false,
  onSelect,
}: CatalogueGridProps) {
  return (
    <div className="flex flex-col gap-2">
      <h3 className="text-sm font-semibold text-slate-700">
        Choose from catalogue
      </h3>
      <div className="grid grid-cols-3 gap-3 sm:grid-cols-6">
        {CATALOGUE.map((item) => {
          const selected = item.id === selectedId;
          return (
            <button
              key={item.id}
              type="button"
              disabled={disabled}
              onClick={() => onSelect(item.id)}
              title={item.name}
              className={`flex flex-col items-center gap-1 rounded-xl border p-2 transition disabled:cursor-not-allowed disabled:opacity-60 ${
                selected
                  ? "border-indigo-400 ring-2 ring-indigo-200"
                  : "border-slate-200 hover:border-indigo-300"
              }`}
            >
              <img
                src={item.imageUrl}
                alt={item.name}
                className="aspect-square w-full rounded-lg object-cover"
              />
              <span className="truncate text-[11px] font-medium text-slate-500">
                {item.name}
              </span>
            </button>
          );
        })}
      </div>
    </div>
  );
}

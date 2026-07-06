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
      <div className="grid grid-cols-2 gap-4 sm:grid-cols-3">
        {CATALOGUE.map((item) => {
          const selected = item.id === selectedId;
          return (
            <button
              key={item.id}
              type="button"
              disabled={disabled}
              onClick={() => onSelect(item.id)}
              className={`group relative flex flex-col overflow-hidden rounded-2xl border-2 bg-white text-left transition hover:-translate-y-0.5 hover:shadow-md disabled:cursor-not-allowed disabled:opacity-60 ${
                selected
                  ? "border-blue-500 ring-2 ring-blue-200"
                  : "border-slate-200 hover:border-blue-300"
              }`}
            >
              {selected && (
                <span className="absolute right-2 top-2 z-10 rounded-full bg-blue-500 px-2 py-0.5 text-[10px] font-semibold text-white">
                  Selected
                </span>
              )}
              <div className="flex aspect-square w-full items-center justify-center bg-slate-50 p-3">
                <img
                  src={item.imageUrl}
                  alt={item.name}
                  className="max-h-full max-w-full object-contain"
                />
              </div>
              <span className="truncate px-3 py-2 text-sm font-medium text-slate-600">
                {item.name}
              </span>
            </button>
          );
        })}
      </div>
    </div>
  );
}

interface RatingControlProps {
  value: number; // escala 0-10
  onChange: (value: number) => void;
}

export default function RatingControl({ value, onChange }: RatingControlProps) {
  return (
    <div className="rating-input">
      <input
        type="range"
        min={0}
        max={10}
        step={0.5}
        value={value}
        onChange={(e) => onChange(Number(e.target.value))}
        aria-label="Escolha uma nota de 0 a 10"
      />
      <span className="rating-value">{value.toFixed(1)}/10</span>
    </div>
  );
}

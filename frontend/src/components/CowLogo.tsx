interface CowLogoProps {
  size?: number;
}

export default function CowLogo({ size = 30 }: CowLogoProps) {
  return (
    <svg width={size} height={size} viewBox="0 0 44 40" aria-hidden="true">
      {/* orelhas */}
      <ellipse cx="6" cy="15" rx="5" ry="7" fill="#f4ede1" transform="rotate(-25 6 15)" />
      <ellipse cx="38" cy="15" rx="5" ry="7" fill="#f4ede1" transform="rotate(25 38 15)" />

      {/* chifres */}
      <path d="M13 7 L11 1" stroke="#d8cdb8" strokeWidth="3" strokeLinecap="round" />
      <path d="M31 7 L33 1" stroke="#d8cdb8" strokeWidth="3" strokeLinecap="round" />

      {/* cabeça */}
      <rect x="6" y="9" width="32" height="27" rx="13" fill="#f4ede1" />

      {/* manchas */}
      <ellipse cx="13" cy="15" rx="3.6" ry="2.8" fill="#20282b" />
      <ellipse cx="31" cy="28" rx="4.6" ry="3.6" fill="#20282b" />

      {/* focinho */}
      <rect x="12" y="25" width="20" height="10" rx="5" fill="#fff8ee" />
      <circle cx="18" cy="30" r="1.3" fill="#20282b" />
      <circle cx="26" cy="30" r="1.3" fill="#20282b" />

      {/* óculos 3D */}
      <path d="M8 21 L3 19" stroke="#111417" strokeWidth="1.6" strokeLinecap="round" />
      <path d="M36 21 L41 19" stroke="#111417" strokeWidth="1.6" strokeLinecap="round" />
      <rect x="19" y="20" width="6" height="2.4" fill="#111417" />
      <rect x="8" y="17" width="11" height="9" rx="2.2" fill="#ff5a5a" fillOpacity="0.8" stroke="#111417" strokeWidth="1.6" />
      <rect x="25" y="17" width="11" height="9" rx="2.2" fill="#57c7f0" fillOpacity="0.8" stroke="#111417" strokeWidth="1.6" />
    </svg>
  );
}

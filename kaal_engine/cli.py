#!/usr/bin/env python3
import argparse
import json
from datetime import datetime, timezone, timedelta
from .kaal import Kaal
from .core.ayanamsha import AyanamshaEngine
from .core.muhurta import MuhurtaEngine, MuhurtaType, MuhurtaRequest, find_marriage_muhurta, find_business_muhurta, find_travel_muhurta

def format_output(data, format_type='human'):
    """Format output data based on specified format"""
    if format_type == 'json':
        return json.dumps(data, indent=2, default=str)
    elif format_type == 'human':
        return format_human_readable(data)
    else:
        return str(data)

def format_human_readable(data, indent=0):
    """Format data in human-readable format"""
    output = []
    prefix = "  " * indent
    
    for key, value in data.items():
        if isinstance(value, dict):
            output.append(f"{prefix}{key.replace('_', ' ').title()}:")
            output.append(format_human_readable(value, indent + 1))
        elif isinstance(value, list):
            output.append(f"{prefix}{key.replace('_', ' ').title()}:")
            for item in value:
                if isinstance(item, dict):
                    output.append(format_human_readable(item, indent + 1))
                else:
                    output.append(f"{prefix}  {item}")
        else:
            formatted_key = key.replace('_', ' ').title()
            if isinstance(value, float):
                output.append(f"{prefix}{formatted_key}: {value:.4f}")
            else:
                output.append(f"{prefix}{formatted_key}: {value}")
    
    return '\n'.join(output)

def cmd_panchang(args):
    """Calculate comprehensive panchang"""
    # Parse date and time
    if args.date and args.date != 'now':
        date_str = args.date
    else:
        date_str = datetime.now().strftime('%Y-%m-%d')
    
    if args.time:
        time_str = args.time
    else:
        time_str = '12:00:00'
    
    dt_str = f"{date_str} {time_str}"
    dt = datetime.strptime(dt_str, '%Y-%m-%d %H:%M:%S')
    dt = dt.replace(tzinfo=timezone.utc)
    
    # Calculate panchang
    kaal = Kaal(args.ephemeris)
    result = kaal.get_panchang(
        lat=args.lat, 
        lon=args.lon, 
        dt=dt, 
        elevation=args.elevation,
        ayanamsha=args.ayanamsha
    )
    
    print(f"Comprehensive Panchang for {dt_str} UTC")
    print(f"Location: {args.lat}°N, {args.lon}°E (Elevation: {args.elevation}m)")
    print(f"Ayanamsha: {args.ayanamsha}")
    print("=" * 60)
    print(format_output(result, args.format))

def cmd_ayanamsha(args):
    """Compare ayanamsha systems"""
    if args.date and args.date != 'now':
        date_str = args.date
    else:
        date_str = datetime.now().strftime('%Y-%m-%d')
    
    dt = datetime.strptime(date_str, '%Y-%m-%d')
    dt = dt.replace(tzinfo=timezone.utc)
    
    kaal = Kaal(args.ephemeris)
    jd_tt = kaal._julian_day(dt)
    
    comparison = kaal.get_ayanamsha_comparison(jd_tt)
    
    print(f"Ayanamsha Comparison for {date_str}")
    print("=" * 50)
    
    # Sort by value
    sorted_systems = sorted(comparison.items(), key=lambda x: x[1])
    
    for system, value in sorted_systems:
        description = kaal.ayanamsha_engine.SUPPORTED_SYSTEMS.get(system, "")
        print(f"{system:15} {value:8.4f}° - {description}")
    
    # Show differences from specified reference
    if args.reference:
        ref_value = comparison.get(args.reference)
        if ref_value:
            print(f"\nDifferences from {args.reference}:")
            for system, value in sorted_systems:
                if system != args.reference:
                    diff = value - ref_value
                    print(f"{system:15} {diff:+8.4f}°")

def cmd_planetary(args):
    """Show planetary positions"""
    if args.date and args.date != 'now':
        date_str = args.date
    else:
        date_str = datetime.now().strftime('%Y-%m-%d')
    
    if args.time:
        time_str = args.time
    else:
        time_str = '12:00:00'
    
    dt_str = f"{date_str} {time_str}"
    dt = datetime.strptime(dt_str, '%Y-%m-%d %H:%M:%S')
    dt = dt.replace(tzinfo=timezone.utc)
    
    kaal = Kaal(args.ephemeris)
    result = kaal.get_panchang(
        lat=args.lat,
        lon=args.lon,
        dt=dt,
        ayanamsha=args.ayanamsha
    )
    
    print(f"Planetary Positions for {dt_str} UTC")
    print(f"Ayanamsha: {args.ayanamsha}")
    print("=" * 60)
    
    if 'graha_positions' in result:
        for planet, data in result['graha_positions'].items():
            print(f"{planet.capitalize():10}")
            print(f"  Longitude: {data['longitude']:8.4f}°")
            print(f"  Rashi:     {data['rashi']}")
            print(f"  Nakshatra: {data['nakshatra']}")
            print()
    
    # Show aspects if requested
    if args.aspects and 'graha_positions' in result:
        aspects = kaal.calculate_planetary_aspects(result['graha_positions'])
        if aspects:
            print("Planetary Aspects:")
            print("-" * 30)
            for aspect_key, aspect_data in aspects.items():
                print(f"{aspect_key}: {aspect_data['aspect']} (orb: {aspect_data['orb']:.2f}°)")

def cmd_muhurta(args):
    """Find auspicious muhurta timings"""
    # Parse dates
    if args.start_date:
        start_date = datetime.strptime(args.start_date, '%Y-%m-%d')
    else:
        start_date = datetime.now()
    
    if args.end_date:
        end_date = datetime.strptime(args.end_date, '%Y-%m-%d')
    else:
        end_date = start_date + timedelta(days=7)  # Default to 7 days
    
    # Set timezone to UTC
    start_date = start_date.replace(tzinfo=timezone.utc)
    end_date = end_date.replace(tzinfo=timezone.utc)
    
    # Initialize engines
    kaal = Kaal(args.ephemeris)
    muhurta_engine = MuhurtaEngine(kaal)
    
    # Convert type to enum
    muhurta_type_map = {
        'marriage': MuhurtaType.MARRIAGE,
        'business': MuhurtaType.BUSINESS,
        'travel': MuhurtaType.TRAVEL,
        'education': MuhurtaType.EDUCATION,
        'property': MuhurtaType.PROPERTY,
        'general': MuhurtaType.GENERAL
    }
    
    muhurta_type = muhurta_type_map[args.type]
    
    # Create request
    request = MuhurtaRequest(
        muhurta_type=muhurta_type,
        start_date=start_date,
        end_date=end_date,
        latitude=args.lat,
        longitude=args.lon,
        duration_minutes=args.duration
    )
    
    # Find muhurtas
    results = muhurta_engine.find_muhurta(request)
    
    # Filter by quality
    quality_filter_map = {
        'excellent': ['excellent'],
        'very_good': ['excellent', 'very_good'],
        'good': ['excellent', 'very_good', 'good'],
        'average': ['excellent', 'very_good', 'good', 'average']
    }
    
    allowed_qualities = quality_filter_map[args.quality]
    filtered_results = [r for r in results if r.quality.value in allowed_qualities]
    
    # Limit results
    limited_results = filtered_results[:args.limit]
    
    print(f"Muhurta Analysis: {args.type.title()} Timings")
    print(f"Location: {args.lat}°N, {args.lon}°E")
    print(f"Period: {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}")
    print(f"Duration: {args.duration} minutes")
    print(f"Minimum Quality: {args.quality.replace('_', ' ').title()}")
    print("=" * 80)
    
    if not limited_results:
        print("No suitable muhurta timings found in the specified period.")
        print("Try:")
        print("- Extending the date range")
        print("- Lowering the quality threshold")
        print("- Checking different muhurta types")
        return
    
    if args.format == 'json':
        # Convert results to JSON-serializable format
        json_results = []
        for result in limited_results:
            json_result = {
                'datetime': result.datetime.isoformat(),
                'quality': result.quality.value,
                'score': result.score,
                'description': result.description,
                'recommendations': result.recommendations,
                'warnings': result.warnings,
                'duration_minutes': result.duration_minutes,
                'factors': result.factors
            }
            json_results.append(json_result)
        
        print(json.dumps(json_results, indent=2))
    else:
        # Human-readable format
        for i, result in enumerate(limited_results, 1):
            print(f"\n{i}. {result.quality.value.replace('_', ' ').title()} Muhurta")
            print(f"   Time: {result.datetime.strftime('%Y-%m-%d %H:%M:%S')} UTC")
            print(f"   Score: {result.score:.1f}/100")
            print(f"   Duration: {result.duration_minutes} minutes")
            print(f"   Description: {result.description}")
            
            if result.recommendations:
                print("   Recommendations:")
                for rec in result.recommendations:
                    print(f"     • {rec}")
            
            if result.warnings:
                print("   Warnings:")
                for warning in result.warnings:
                    print(f"     ⚠ {warning}")
            
            # Show key factors
            print("   Key Factors:")
            tithi_factor = result.factors.get('tithi', {})
            if tithi_factor:
                print(f"     Tithi: {tithi_factor.get('tithi_name', 'Unknown')} ({'Favorable' if tithi_factor.get('favorable') else 'Neutral'})")
            
            nakshatra_factor = result.factors.get('nakshatra', {})
            if nakshatra_factor:
                print(f"     Nakshatra: {nakshatra_factor.get('nakshatra', 'Unknown')} ({'Favorable' if nakshatra_factor.get('favorable') else 'Neutral'})")
            
            vara_factor = result.factors.get('vara', {})
            if vara_factor:
                print(f"     Day: {vara_factor.get('vara', 'Unknown')} ({'Favorable' if vara_factor.get('favorable') else 'Neutral'})")
            
            print("-" * 60)

def main():
    parser = argparse.ArgumentParser(description='Brahmakaal - Advanced Vedic Ephemeris Engine')
    
    # Global arguments
    parser.add_argument('--ephemeris', type=str, default='data/de441.bsp', 
                       help='Path to ephemeris file (default: data/de441.bsp)')
    parser.add_argument('--format', choices=['human', 'json'], default='human',
                       help='Output format (default: human)')
    
    # Create subparsers
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Panchang command
    panchang_parser = subparsers.add_parser('panchang', help='Calculate comprehensive panchang')
    panchang_parser.add_argument('--lat', type=float, required=True, help='Latitude in degrees')
    panchang_parser.add_argument('--lon', type=float, required=True, help='Longitude in degrees')
    panchang_parser.add_argument('--date', type=str, default='now', help='Date in YYYY-MM-DD format (default: today)')
    panchang_parser.add_argument('--time', type=str, help='Time in HH:MM:SS format (default: 12:00:00)')
    panchang_parser.add_argument('--elevation', type=float, default=0.0, help='Elevation in meters (default: 0)')
    panchang_parser.add_argument('--ayanamsha', type=str, default='LAHIRI',
                                choices=['LAHIRI', 'RAMAN', 'KRISHNAMURTI', 'YUKTESHWAR', 'SURYASIDDHANTA'],
                                help='Ayanamsha system (default: LAHIRI)')
    panchang_parser.set_defaults(func=cmd_panchang)
    
    # Ayanamsha command
    ayanamsha_parser = subparsers.add_parser('ayanamsha', help='Compare ayanamsha systems')
    ayanamsha_parser.add_argument('--date', type=str, default='now', help='Date in YYYY-MM-DD format (default: today)')
    ayanamsha_parser.add_argument('--reference', type=str, default='LAHIRI',
                                 help='Reference ayanamsha for differences (default: LAHIRI)')
    ayanamsha_parser.set_defaults(func=cmd_ayanamsha)
    
    # Planetary command
    planetary_parser = subparsers.add_parser('planets', help='Show planetary positions')
    planetary_parser.add_argument('--lat', type=float, required=True, help='Latitude in degrees')
    planetary_parser.add_argument('--lon', type=float, required=True, help='Longitude in degrees')
    planetary_parser.add_argument('--date', type=str, default='now', help='Date in YYYY-MM-DD format (default: today)')
    planetary_parser.add_argument('--time', type=str, help='Time in HH:MM:SS format (default: 12:00:00)')
    planetary_parser.add_argument('--ayanamsha', type=str, default='LAHIRI',
                                 choices=['LAHIRI', 'RAMAN', 'KRISHNAMURTI', 'YUKTESHWAR', 'SURYASIDDHANTA'],
                                 help='Ayanamsha system (default: LAHIRI)')
    planetary_parser.add_argument('--aspects', action='store_true', help='Show planetary aspects')
    planetary_parser.set_defaults(func=cmd_planetary)
    
    # Muhurta command
    muhurta_parser = subparsers.add_parser('muhurta', help='Find auspicious muhurta timings')
    muhurta_parser.add_argument('--type', type=str, required=True,
                               choices=['marriage', 'business', 'travel', 'education', 'property', 'general'],
                               help='Type of muhurta to find')
    muhurta_parser.add_argument('--lat', type=float, required=True, help='Latitude in degrees')
    muhurta_parser.add_argument('--lon', type=float, required=True, help='Longitude in degrees')
    muhurta_parser.add_argument('--start-date', type=str, help='Start date in YYYY-MM-DD format (default: today)')
    muhurta_parser.add_argument('--end-date', type=str, help='End date in YYYY-MM-DD format (default: 7 days from start)')
    muhurta_parser.add_argument('--duration', type=int, default=60, help='Duration in minutes (default: 60)')
    muhurta_parser.add_argument('--limit', type=int, default=10, help='Maximum number of results (default: 10)')
    muhurta_parser.add_argument('--quality', type=str, default='good',
                               choices=['excellent', 'very_good', 'good', 'average'],
                               help='Minimum quality level (default: good)')
    muhurta_parser.set_defaults(func=cmd_muhurta)
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    try:
        args.func(args)
    except Exception as e:
        print(f"Error: {e}")
        return 1
    
    return 0

if __name__ == '__main__':
    exit(main()) 
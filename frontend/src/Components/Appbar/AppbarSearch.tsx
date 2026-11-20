import {useState} from 'react'
import {Autocomplete,InputAdornment,TextField} from '@mui/material'
import SearchRoundedIcon from '@mui/icons-material/SearchRounded'
import {useSelector} from 'react-redux'
import {useNavigate} from 'react-router-dom'
import {drawerGroups,drawerItems,canAccessDrawerItem} from '../Drawer/DrawerItems'
import {selectRole} from '../../redux/RoleSlice'
import {usePanelSettings} from '../../Core/PanelSettingsContext'
import featureOptions from '../../Pages/Settings/featureOptions.json'

export default function AppbarSearch({placeholder,mobile}:{placeholder?:string;mobile?:boolean}){
 const role=useSelector(selectRole),navigate=useNavigate(),{settings}=usePanelSettings()
 const [section,setSection]=useState(''),[input,setInput]=useState('')
 const featureForLink=Object.fromEntries(featureOptions.map(x=>[x.link,x.key]))
 const available=drawerItems.filter(item=>!item.disabled&&canAccessDrawerItem(item,role)&&settings.features[featureForLink[item.link]]!==false)
 const groups=drawerGroups.filter(group=>available.some(item=>item.groupId===group.id))
 return <div className="panel-search-shell">
 <Autocomplete className="panel-search-input" size="small" options={available.filter(item=>!section||item.groupId===section)} getOptionLabel={item=>item.title} value={null} inputValue={input} onInputChange={(_,value)=>setInput(value)} noOptionsText="نتیجه‌ای پیدا نشد" onChange={(_,item)=>{if(item){navigate(`/${item.link}`);setInput('')}}} forcePopupIcon={false} renderInput={params=><TextField {...params} placeholder={placeholder||`جستجو در ${settings.general.shortName} ...`} inputProps={{...params.inputProps,'aria-label':'جستجو در صفحات پنل'}} InputProps={{...params.InputProps,startAdornment:<InputAdornment position="start"><SearchRoundedIcon/></InputAdornment>}}/>}/>
 <select className="panel-search-section" aria-label="بخش جستجو" value={section} onChange={e=>{setSection(e.target.value);setInput('')}}><option value="">همه بخش‌ها</option>{groups.map(group=><option key={group.id} value={group.id}>{group.title}</option>)}</select>
 </div>
}

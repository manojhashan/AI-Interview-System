
import React, { useState } from 'react';
import { ResumeData, ExperienceEntry } from '../types';
import { Plus, Trash2, Save, X, Briefcase, GraduationCap, Award, Rocket, Wrench, Calendar } from 'lucide-react';

interface ResumeFormProps {
  existingResume?: ResumeData;
  onSave: (data: ResumeData) => void;
  onCancel: () => void;
}

const ResumeForm: React.FC<ResumeFormProps> = ({ existingResume, onSave, onCancel }) => {
  const currentYear = new Date().getFullYear();
  const years = Array.from({ length: 50 }, (_, i) => (currentYear - i).toString());
  const endYears = ['Present', ...years];

  const [resumeTitle, setResumeTitle] = useState(existingResume?.resumeTitle || '');
  const [skills, setSkills] = useState<string[]>(existingResume?.skills || ['']);
  const [certificates, setCertificates] = useState<string[]>(existingResume?.certificates || ['']);
  const [education, setEducation] = useState<string[]>(existingResume?.education || ['']);
  const [projects, setProjects] = useState<string[]>(existingResume?.projects || ['']);
  const [experience, setExperience] = useState<ExperienceEntry[]>(
    existingResume?.experience || [{ job_role: '', startYear: currentYear.toString(), endYear: 'Present' }]
  );

  const [saving, setSaving] = useState(false);

  const addItem = (setter: any, list: any[], defaultValue: any) => {
    setter([...list, defaultValue]);
  };

  const updateItem = (setter: any, list: any[], index: number, value: any) => {
    const newList = [...list];
    newList[index] = value;
    setter(newList);
  };

  const removeItem = (setter: any, list: any[], index: number) => {
    if (list.length <= 1) return;
    const newList = [...list];
    newList.splice(index, 1);
    setter(newList);
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!resumeTitle) {
      alert("Please enter a Resume Title (Job Role)");
      return;
    }
    setSaving(true);
    const data: ResumeData = {
      id: existingResume?.id || Math.random().toString(36).substr(2, 9),
      resumeTitle,
      skills: skills.filter(s => s.trim() !== ''),
      certificates: certificates.filter(c => c.trim() !== ''),
      education: education.filter(e => e.trim() !== ''),
      projects: projects.filter(p => p.trim() !== ''),
      experience: experience.filter(exp => exp.job_role.trim() !== '')
    };
    
    setTimeout(() => {
      onSave(data);
      setSaving(false);
    }, 800);
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-8 animate-in fade-in slide-in-from-bottom-4 duration-500">
      {/* Header Info */}
      <div className="bg-slate-900 border border-slate-800 p-8 rounded-3xl">
        <label className="block text-xs font-bold text-slate-500 uppercase tracking-widest mb-3">Resume Title / Target Job Role</label>
        <input 
          required
          value={resumeTitle}
          maxLength={100}
          onChange={(e) => setResumeTitle(e.target.value)}
          placeholder="e.g. Senior Frontend Engineer"
          // 13. Character Limit Enforcement (Assumed by UI/HTML constraints or validation)
          className="w-full bg-slate-950 border border-white/5 rounded-2xl py-4 px-6 text-xl font-bold focus:border-blue-500 outline-none transition-all"
        />
      </div>

      <div className="grid md:grid-cols-2 gap-8">
        {/* Skills */}
        <Section 
          title="Skills" 
          icon={<Wrench size={18} className="text-blue-400" />} 
          label="skill"
          items={skills}
          maxLength={50}
          onAdd={() => addItem(setSkills, skills, '')}
          onUpdate={(idx, val) => updateItem(setSkills, skills, idx, val)}
          onRemove={(idx) => removeItem(setSkills, skills, idx)}
        />

        {/* Certificates */}
        <Section 
          title="Certificates" 
          icon={<Award size={18} className="text-emerald-400" />} 
          label="certificate_name"
          items={certificates}
          maxLength={100}
          onAdd={() => addItem(setCertificates, certificates, '')}
          onUpdate={(idx, val) => updateItem(setCertificates, certificates, idx, val)}
          onRemove={(idx) => removeItem(setCertificates, certificates, idx)}
        />

        {/* Education */}
        <Section 
          title="Education" 
          icon={<GraduationCap size={18} className="text-purple-400" />} 
          label="Course_name"
          items={education}
          maxLength={200}
          onAdd={() => addItem(setEducation, education, '')}
          onUpdate={(idx, val) => updateItem(setEducation, education, idx, val)}
          onRemove={(idx) => removeItem(setEducation, education, idx)}
        />

        {/* Projects */}
        <Section 
          title="Projects" 
          icon={<Rocket size={18} className="text-orange-400" />} 
          label="Project_title"
          items={projects}
          maxLength={500}
          onAdd={() => addItem(setProjects, projects, '')}
          onUpdate={(idx, val) => updateItem(setProjects, projects, idx, val)}
          onRemove={(idx) => removeItem(setProjects, projects, idx)}
        />
      </div>

      {/* Experience */}
      <div className="bg-slate-900 border border-slate-800 p-8 rounded-3xl">
        <div className="flex justify-between items-center mb-6">
           <h3 className="text-lg font-bold flex items-center gap-2"><Briefcase size={20} className="text-pink-400" /> Work Experience</h3>
           <button type="button" onClick={() => addItem(setExperience, experience, { job_role: '', startYear: currentYear.toString(), endYear: 'Present' })} className="p-2 bg-slate-800 hover:bg-slate-700 rounded-full transition-colors">
             <Plus size={20} />
           </button>
        </div>
        <div className="space-y-6">
           {experience.map((exp, idx) => (
             <div key={idx} className="flex flex-col md:flex-row gap-4 items-start bg-slate-950/40 p-5 rounded-2xl border border-white/5 shadow-inner">
                <div className="flex-1 space-y-4 w-full">
                  <div>
                    <label className="block text-[10px] font-black text-slate-500 uppercase tracking-widest mb-1.5 ml-1">Job Role</label>
                    <input 
                      value={exp.job_role} 
                      maxLength={100}
                      onChange={(e) => {
                        const newExp = [...experience];
                        newExp[idx].job_role = e.target.value;
                        setExperience(newExp);
                      }}
                      placeholder="e.g. Software Engineer" 
                      className="w-full bg-slate-950 border border-white/5 rounded-xl py-3 px-4 text-sm outline-none focus:border-pink-500/50" 
                    />
                  </div>
                  
                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <label className="block text-[10px] font-black text-slate-500 uppercase tracking-widest mb-1.5 ml-1 flex items-center gap-1">
                        <Calendar size={10} /> Start Year
                      </label>
                      <select 
                        value={exp.startYear}
                        onChange={(e) => {
                          const newExp = [...experience];
                          newExp[idx].startYear = e.target.value;
                          setExperience(newExp);
                        }}
                        className="w-full bg-slate-950 border border-white/5 rounded-xl py-3 px-4 text-sm outline-none focus:border-pink-500/50 appearance-none cursor-pointer"
                      >
                        {years.map(y => <option key={y} value={y}>{y}</option>)}
                      </select>
                    </div>
                    <div>
                      <label className="block text-[10px] font-black text-slate-500 uppercase tracking-widest mb-1.5 ml-1 flex items-center gap-1">
                        <Calendar size={10} /> End Year
                      </label>
                      <select 
                        value={exp.endYear}
                        onChange={(e) => {
                          const newExp = [...experience];
                          newExp[idx].endYear = e.target.value;
                          setExperience(newExp);
                        }}
                        className="w-full bg-slate-950 border border-white/5 rounded-xl py-3 px-4 text-sm outline-none focus:border-pink-500/50 appearance-none cursor-pointer"
                      >
                        {endYears.map(y => <option key={y} value={y}>{y}</option>)}
                      </select>
                    </div>
                  </div>
                </div>
                <button 
                  type="button" 
                  onClick={() => removeItem(setExperience, experience, idx)} 
                  className="p-3 text-red-500 hover:bg-red-500/10 rounded-xl transition-all self-end md:self-center"
                >
                  <Trash2 size={20} />
                </button>
             </div>
           ))}
        </div>
      </div>

      <div className="flex justify-end gap-4">
        <button type="button" onClick={onCancel} className="px-8 py-3 bg-slate-800 hover:bg-slate-700 rounded-xl font-bold transition-all">Cancel</button>
        <button
          type="submit"
          disabled={saving}
          className="bg-blue-600 hover:bg-blue-500 text-white px-10 py-3 rounded-xl font-bold flex items-center gap-2 shadow-lg shadow-blue-600/20 transition-all"
        >
          {saving ? 'Saving...' : <><Save size={20} /> Save Resume Profile</>}
        </button>
      </div>
    </form>
  );
};

const Section = ({ title, icon, label, items, maxLength, onAdd, onUpdate, onRemove }: any) => (
  <div className="bg-slate-900 border border-slate-800 p-6 rounded-3xl h-full flex flex-col">
    <div className="flex justify-between items-center mb-6">
       <h3 className="text-lg font-bold flex items-center gap-2">{icon} {title}</h3>
       <button type="button" onClick={onAdd} className="p-1.5 bg-slate-800 hover:bg-slate-700 rounded-full transition-colors">
         <Plus size={18} />
       </button>
    </div>
    <div className="space-y-3 flex-1">
       {items.map((item: string, idx: number) => (
         <div key={idx} className="flex gap-2">
           <input 
             value={item} 
             maxLength={maxLength}
             onChange={(e) => onUpdate(idx, e.target.value)}
             placeholder={`${label}...`} 
             className="flex-1 bg-slate-950 border border-white/5 rounded-xl py-2.5 px-4 text-sm outline-none focus:border-blue-500/30" 
           />
           <button type="button" onClick={() => onRemove(idx)} className="p-2.5 text-slate-500 hover:text-red-500 hover:bg-red-500/10 rounded-xl transition-all">
             <X size={16} />
           </button>
         </div>
       ))}
    </div>
  </div>
);

export default ResumeForm;
